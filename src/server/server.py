#!/usr/bin/python

import zmq
from zmq.eventloop import zmqstream, ioloop
from tornado.web import StaticFileHandler

ioloop.install()

import os
import tornado.ioloop
import tornado.web
import tornado.websocket
import json

_sockets = []
_context = zmq.Context().instance()
_output_socket = _context.socket(zmq.PUSH)
_output_socket.connect("tcp://192.168.0.105:8890")

class UISocket(tornado.websocket.WebSocketHandler):

    def open(self):
        print "Open!"
        _sockets.append(self)

    def on_close(self):
        print "Closed!"
        _sockets.remove(self)

    def on_message(self, message):
        try:
            _output_socket.send_string(message)
            print message
        except Exception as ex:
            print ex.message


class Listener():

    def __init__(self):
        '''
        Constructor
        '''
        self.context = zmq.Context().instance()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://192.168.0.105:8891")
        self.socket.connect("tcp://192.168.0.105:8892")
        self.socket.connect("tcp://192.168.0.105:8893")
        self.socket.setsockopt(zmq.SUBSCRIBE,"scan")
        self.socket.setsockopt(zmq.SUBSCRIBE,"dropbox")
        self.socket.setsockopt(zmq.SUBSCRIBE,"grid_publish")
        self.loop = ioloop.IOLoop.instance()
        self.stream = zmqstream.ZMQStream(self.socket)
        self.stream.on_recv(self.handle_msg)

    def handle_msg(self, msg):
        for sock in _sockets:
            sock.write_message(unicode(msg[1]))

class IndexJs(tornado.web.RequestHandler):

    def get(self):
        self.write('''var index = {};
        index.socket_uri = "ws://%s/socket";
        $.getScript("scripts/index.js");''' % (self.request.host))


class UIHandler(tornado.web.RequestHandler):

    def get(self):
        pass

if __name__ == "__main__":
    listener = Listener()
    settings = {"static_path":os.path.join(os.path.dirname(__file__),"static")}
    app = tornado.web.Application([(r"/settings.js",IndexJs),
                                   (r"/socket", UISocket),
                                   (r"/*.png", StaticFileHandler)],
                                  [dict(path=settings['static_path'])],
                                  **settings)
    app.listen(9999)
    tornado.ioloop.IOLoop.instance().start()