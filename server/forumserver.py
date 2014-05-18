#!/usr/bin/python
import os
import sys

root_dir = os.path.join('/', 'home', 'igor', 'Projects', 'python', 'forum')
os.chdir(root_dir)
sys.path.append(root_dir)


import functools
import json
import logging
import threading

import tornado.web
import tornado.gen
import tornado.ioloop
from tornado.options import define, options

from api import api_executor
from api.util.response_helpers import *
from api.util.DataService import DataService

ds = DataService()

def async_task(func):
    @functools.wraps(func)
    def async_func(*args, **kwargs):
        th = threading.Thread(target=func, args=args, kwargs=kwargs)
        th.start()

    return async_func


class ThreadMixin(tornado.web.RequestHandler):
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
        self.res = api_executor.execute(ds, self.entity, self.action, self.data)

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


class ClearHandler(ThreadMixin):
    res = None

    def _worker(self):
        self.res = api_executor.clear_db()

    @tornado.web.asynchronous
    def get(self):
        self.send_error(405)

    @tornado.web.asynchronous
    def post(self):
        self.start_worker()


define('port', type=int, default=9001)


def main():
    tornado.options.parse_command_line()

    application = tornado.web.Application([
        (r"/(\S+)/(\S+)", Handler),
        (r"/clear/", ClearHandler),
    ])

    logging.info("Server started on port %s", options.port)
    application.listen(options.port)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        ds.close_all()
        logging.info("Server stopped")


if __name__ == "__main__":
    main()
