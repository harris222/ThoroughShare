import tornado.web, tornado.websocket, tornado.escape

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    roomMembers = []
    chat_history = []
    def on_message(self, message):
        print("Websocket message",message)
        message = tornado.escape.json_decode(message)
        if 'recast' in message:
            messageOut = {'identity': message['identity'], 'message': message['message']}
            for i in WebSocketHandler.roomMembers:
                i.write_message(messageOut)

            WebSocketHandler.chat_history.append(messageOut)


    def open(self, *args, **kwargs):
        print("Websocket opened")
        WebSocketHandler.roomMembers.append(self)

        for i in WebSocketHandler.chat_history:
            self.write_message(i)

    def on_close(self):
        print("Websocket closed")
        WebSocketHandler.roomMembers.remove(self)

