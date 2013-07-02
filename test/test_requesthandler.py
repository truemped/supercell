# vim: set fileencoding=utf-8 :
#
# Copyright (c) 2013 Daniel Truemper <truemped at googlemail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
from __future__ import absolute_import, division, print_function, with_statement

from schematics.models import Model
from schematics.types import StringType

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

import supercell.api as s
from supercell.api import (RequestHandler, provides, consumes)


class SimpleMessage(Model):
    doc_id = StringType()
    message = StringType()


@provides('application/json')
class MyHandler(RequestHandler):

    @gen.coroutine
    def get(self, *args, **kwargs):
        raise s.Return(SimpleMessage(doc_id='test123', message='A test'))


@provides('application/json', default=True)
class MyHandlerWithDefault(RequestHandler):

    @gen.coroutine
    def get(self, *args, **kwargs):
        raise s.Return(SimpleMessage(doc_id='test123', message='A test'))


@consumes('application/json', SimpleMessage)
class MyEchoHandler(RequestHandler):

    @gen.coroutine
    def get(self, *args, **kwargs):
        q = self.get_argument('q')
        # query solr:
        raise s.Return(SimpleMessage(doc_id='test456', message='q: %s' % q))

    @gen.coroutine
    def post(self, *args, **kwargs):
        model = kwargs.get('model')
        # do something with model
        raise s.OkCreated()


class TestSimpleRequestHandler(AsyncHTTPTestCase):

    def get_app(self):
        app = Application([
            ('/test', MyHandler),
            ('/test_default', MyHandlerWithDefault),
            ('/test_post', MyEchoHandler),
        ])
        return app

    def get_new_ioloop(self):
        return IOLoop.instance()

    def test_simple_handler(self):
        response = self.fetch('/test', headers={'Accept': 'application/json'})
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body,
                         '{"message": "A test", "doc_id": "test123"}')

    def test_handler_without_accept(self):
        response = self.fetch('/test')
        self.assertEqual(response.code, 406)

    def test_default_handler(self):
        response = self.fetch('/test_default')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body,
                         '{"message": "A test", "doc_id": "test123"}')

    def test_handler_with_missing_provider(self):
        response = self.fetch('/test', headers={'Accept':
            'application/vnd.supercell+xml'})
        self.assertEqual(response.code, 406)

    def test_post_handler(self):
        response = self.fetch('/test_post', method='POST',
                              headers={'Content-Type': 'application/json'},
                              body='{"message": "Simple message"}')
        self.assertEqual(response.code, 201)
