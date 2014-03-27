import functools
import json
import logging
import threading
from api import api_executor
from api.util.response_helpers import *

import tornado.web
import tornado.gen
import tornado.ioloop
from tornado.options import define, options


def async_task(func):
    @functools.wraps(func)
    def async_func(*args, **kwargs):
        th = threading.Thread(target=func, args=args, kwargs=kwargs)
        th.start()
    return async_func


class Handler(tornado.web.RequestHandler):
    @async_task
    def retriever(self, entity, action, data, callback):
        res = api_executor.execute(entity, action, data)
        callback(res)

    @tornado.gen.coroutine
    def get(self, entity, action):
        data = parse_get(self.request.arguments)
        response = yield tornado.gen.Task(self.retriever, entity, action, data)
        self.finish(response)

    @tornado.gen.coroutine
    def post(self, entity, action):
        data = json.loads(self.request.body, encoding='utf-8')
        response = yield tornado.gen.Task(self.retriever, entity, action, data)
        self.finish(response)


define('port', type=int, default=8888)


def main():
    tornado.options.parse_command_line()

    application = tornado.web.Application([
        (r"/(\S+)/(\S+)", Handler),
    ])

    logging.info("Server started on port %s", options.port)
    application.listen(options.port)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.info("Server stopped")


if __name__ == "__main__":
    main()