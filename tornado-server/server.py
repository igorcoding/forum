import json
import logging
import threading
import time
from api import api_executor
from api.util.response_helpers import *

from tornado import web
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options


class ThreadMixin(web.RequestHandler):
    def start_worker(self):
        threading.Thread(target=self.worker).start()

    def _worker(self):
        raise NotImplementedError("Abstract method")

    def worker(self):
        try:
            self._worker()
        except tornado.web.HTTPError, e:
            self.set_status(e.status_code)
        except:
            logging.error("_worker problem", exc_info=True)
            self.set_status(500)
        tornado.ioloop.IOLoop.instance().add_callback(self.async_callback(self.results))

    def results(self):
        if self.get_status() != 200:
            self.send_error(self.get_status())
            return
        if hasattr(self, 'res') and self.res is not None:
            self.finish(self.res)
            return
        if hasattr(self, 'redir'):
            self.redirect(self.redir)
            return
        self.send_error(500)


class Handler(ThreadMixin):
    entity = None
    action = None
    data = None
    res = None

    def _worker(self):
        self.res = api_executor.execute(self.entity, self.action, self.data)

    @tornado.web.asynchronous
    def get(self, entity, action):
        self.entity = entity
        self.action = action
        self.data = parse_get(self.request.arguments)
        self.start_worker()

    @tornado.web.asynchronous
    def post(self, entity, action):
        self.entity = entity
        self.action = action
        self.data = json.loads(self.request.body, encoding='utf-8')
        self.start_worker()

define('port', type=int, default=8888)


def main():
    tornado.options.parse_command_line()

    application = tornado.web.Application([
        (r"/(\S+)/(\S+)", Handler),
    ])

    logging.info("Server started on port %s", options.port)
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()