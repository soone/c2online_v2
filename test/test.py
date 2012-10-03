import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("other")
		self.write("Hello, world")

class StoryHandler(tornado.web.RequestHandler):
	def get(self, story_id):
		self.write("You requested the story " + story_id)

class MyFormHandler(tornado.web.RequestHandler):
	def get(self):
		self.write('<html><body><form action="/myform" method="post">'
				'<input type="text" name="message" />'
				'<input type="submit" value="submit" />'
				'</form></body></html>')
		raise tornado.web.HTTPError(403)

	def post(self):
		self.set_header("Content-Type", "text/plain")
		self.write("You wrote " + self.get_argument("message"))

application = tornado.web.Application([
		(r"/", MainHandler),
		(r"/story/([0-9]+)", StoryHandler),
		(r"/myform", MyFormHandler),
		])

if __name__ == "__main__":
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
