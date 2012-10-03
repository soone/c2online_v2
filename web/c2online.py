#/bin/env python
#-*-coding:utf-8-*-

import os.path
import re
import tornado.web
import tornado.auth
import tornado.database
import tornado.ioloop
import tornado.options
import tornado.httpserver

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define("mysqlHost", default="127.0.0.1:3306", help="c2online database host")
define("mysqlDb", default="c2online", help="c2online database name")
define("mysqlUser", default="root", help="c2online database user")
define("mysqlPass", default="123456", help="c2online database password")

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [(r"/", MainHandler)]
		settings = dict(
			title = u"C2online",
			template_path = os.path.join(os.path.dirname(__file__), "templates"),
			static_path = os.path.join(os.path.dirname(__file__), "static"),
			xsrf_cookies = True,
			cookie_secret = "C2online",
			login_url = "/auth/login",
			authescape = None,
		)

		tornado.web.Application.__init__(self, handlers, **settings)

		self.db = tornado.database.Connection(
			host = options.mysqlHost, database = options.mysqlDb,
			user = options.mysqlUser, password = options.mysqlPass
		)

class BaseHandler(tornado.web.RequestHandler):
	@property
	def db(self):
		return self.application.db

	def get_current_user(self):
		userId = self.get_secure_cookie("user")
		if not userId: return None
		return self.db.get("SELECT adm_user, adm_auth FROM c2_admin WHERE adm_id = %s AND adm_status = 1" % int(userId))

class MainHandler(BaseHandler):
	def get(self):
		self.render("index.html")


if __name__ == "__main__":
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
