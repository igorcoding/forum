from functools import wraps
import json
import logging
import threading
import time
from api import api_executor
from api.util.response_helpers import *

from tornado import web, gen
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options


def async_task(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        th = threading.Thread(target=func, args=args, kwargs=kwargs)
        th.start()
    return async_func


class Handler(web.RequestHandler):
    entity = None
    action = None
    data = None

    @async_task
    def retriever(self, callback):
        res = api_executor.execute(self.entity, self.action, self.data)
        callback(res)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, entity, action):
        self.entity = entity
        self.action = action
        self.data = parse_get(self.request.arguments)
        response = yield tornado.gen.Task(self.retriever)
        self.finish(response)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, entity, action):
        self.entity = entity
        self.action = action
        self.data = json.loads(self.request.body, encoding='utf-8')
        response = yield tornado.gen.Task(self.retriever)
        self.finish(response)

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