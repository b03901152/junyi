#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2
print('os.path.dirname(__file__)',os.path.dirname(__file__))
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        print('MainPage get')
        bookname = self.request.get('bookname','default_bookname')

        entryss_query = Entry.query( ancestor =  ndb.Key('bookname', bookname) ).order(-Entry.date)
        entrys = entryss_query.fetch(10)
        lists=[]
        for i in entrys:
            lists.append(i)
        print lists
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            email=users.get_current_user().email()
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            email = ""
        template_value={
            'bookname':bookname,
            'user':user,
            'lists':lists,
            'url':url,
            'url_linktext':url_linktext,
            'email':email,
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_value))

    def post(self):
        print('MainPage post')

class Author(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)

class Entry(ndb.Model):
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class LoginPage(webapp2.RequestHandler):

    def get(self):
        print('CheckPage POST')
        template = JINJA_ENVIRONMENT.get_template('LoginPage.html')
        self.response.write(template.render())

    def post(self):
        name = self.request.get('name')
        email = self.request.get('email')
        print('CheckPage GET')

class Api(webapp2.RequestHandler):

    def post(self):
        print('Api post')
        bookname = self.request.get('bookname')
        content = self.request.get('content')
        if 'Tiananmen' in content:
            self.redirect('/?bookname=' + bookname)
            return
        author = Author()
        author.identity=users.get_current_user().user_id()
        author.email=users.get_current_user().email()
        entry = Entry( parent = ndb.Key('bookname', bookname) )
        entry.content = content
        entry.author = author
        entry.put()
        self.redirect('/?bookname=' + bookname)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/login',LoginPage),
    ('/api',Api),
], debug=True)

