import tornado.httpserver, tornado.ioloop, tornado.web

import httpServerTornado, websocketServerTornado, os

if __name__ == "__main__":

    settings = dict(
        ssl_options={
            "certfile": os.path.join('../certs/mycert.pem'),
            "keyfile": os.path.join('../certs/mykey.key')
        },
    )

    application = tornado.web.Application(handlers=[
        (r"/", httpServerTornado.MainHandler),   (r"/ws", websocketServerTornado.WebSocketHandler)], static_path='../static/', cookie_secret="XBvhtWJQ$jJDaMEegRmg8pel9cRCmtg")

    sv = tornado.httpserver.HTTPServer(application, **settings)
    sv.listen(443)
    tornado.ioloop.IOLoop.current().start()
