import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))


class Entry(db.Model):
	title = db.StringProperty(required = True)
	body = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)



class BlogHandler(Handler):
    def get(self):
    	entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC LIMIT 5")
    	self.render('blog.html', entries=entries)


class NewPostHandler(Handler):
    def render_form(self, title="", body="", error=""):
    	self.render('newpost.html', title=title, body=body, error=error)

    def get(self):
    	self.render_form()

    def post(self):
		title = self.request.get("title")
		body = self.request.get("body")
		if title and body:
			e = Entry(title=title, body=body)
			e.put() #put() method stores the object in the database

			#self.redirect("/blog")
			self.redirect("/blog/" + str(e.key().id()) )
		else:
			error = "We need both a title and a blog post!"
			self.render_form(title, body, error)

class ViewPostHandler(Handler):
	def get(self, id):
		id = int(id)
		entry = Entry.get_by_id(id)
		title = entry.title
		body = entry.body
		self.render('viewpost.html', title=title, body=body)


app = webapp2.WSGIApplication([
    ('/blog', BlogHandler),
    ('/newpost', NewPostHandler),
    (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
], debug=True)
