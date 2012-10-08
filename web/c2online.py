#/bin/env python
#-*-coding:utf

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
		handlers = [
			(r"/", MainHandler),
			(r"/auth/login[\/]?", LoginHandler),
			(r"/auth/logout[\/]?", LogoutHandler),
		]
		settings = dict(
			title = u"C2online",
			template_path = os.path.join(os.path.dirname(__file__), "templates"),
			static_path = os.path.join(os.path.dirname(__file__), "static"),
			xsrf_cookies = False,
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
		return self.db.get("SELECT adm_id, adm_user, adm_auth FROM c2_admin WHERE adm_id = %s AND adm_status = 1" % int(userId))

class MainHandler(BaseHandler):
	def get(self):
		self.render("index.html")

class LoginHandler(BaseHandler):
	def post(self):
		user = tornado.escape.xhtml_escape(self.get_argument("user", None))
		pwd = self.get_argument("pass", None)
		if user and pwd:
			uPwd = "%s%s" % (user, pwd)
			uInfo = self.db.get("SELECT adm_id, adm_user, adm_auth FROM c2_admin WHERE adm_user = \"%s\" AND adm_status = 1" % user)
			if uInfo:
				self.set_secure_cookie("user", str(uInfo["adm_id"]))
				self.write(tornado.escape.json_encode({"uInfo" : [uInfo["adm_id"], uInfo["adm_user"], uInfo["adm_auth"]]}))
			else:
				self.write(tornado.escape.json_encode({"res" : 0, "msg" : u"帐号或密码错误"}))
		else:
			self.write(tornado.escape.json_encode({"res" : 0, "msg" : u"帐号或密码错误"}))

class LogoutHandler(tornado.web.RequestHandler):
	def post(self):
		print 'test'

if __name__ == "__main__":
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
