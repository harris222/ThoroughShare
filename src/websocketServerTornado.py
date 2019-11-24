import tornado.web, tornado.websocket

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def on_message(self, message):
        print("Websocket message",message)

    def open(self, *args, **kwargs):
        print("Websocket opened")

    def on_close(self):
        print("Websocket closed")

