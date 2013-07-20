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

from collections import defaultdict
from datetime import timedelta

import sys
if sys.version_info > (2, 7):
    from unittest import TestCase
else:
    from unittest2 import TestCase

from nose.tools import raises
from schematics.models import Model
from schematics.types import StringType

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

import supercell.api as s
from supercell.api import (RequestHandler, provides, consumes, MediaType)


class TestConsumesDecorator(TestCase):
    '''Test the consumes decorator.'''

    @raises(AssertionError)
    def test_on_non_class(self):

        @consumes(MediaType.ApplicationJson, object)
        def get():
            pass

    def test_simple_consumes_decorator_with_post(self):

        @consumes(MediaType.ApplicationJson, object)
        class MyHandler(RequestHandler):

            _CONS_CONTENT_TYPES = defaultdict(list)

            def post(self):
                pass

        self.assertTrue(hasattr(MyHandler, '_CONS_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._CONS_CONTENT_TYPES), 1)
        self.assertTrue(MediaType.ApplicationJson in MyHandler._CONS_CONTENT_TYPES)
        content_type = MyHandler._CONS_CONTENT_TYPES[MediaType.ApplicationJson][0]
        self.assertEqual(content_type.content_type, MediaType.ApplicationJson)
        self.assertIsNone(content_type.vendor)
        self.assertIsNone(content_type.version)
        self.assertEqual(MyHandler._CONS_MODEL[content_type], object)

    def test_consumes_decorator_with_vendor_info(self):

        @consumes(MediaType.ApplicationJson, object, vendor='ficture.light',
                  version=1.0)
        class MyHandler(RequestHandler):

            def post(self):
                pass

        self.assertTrue(hasattr(MyHandler, '_CONS_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._CONS_CONTENT_TYPES), 1)
        self.assertTrue(MediaType.ApplicationJson in MyHandler._CONS_CONTENT_TYPES)
        content_type = MyHandler._CONS_CONTENT_TYPES[MediaType.ApplicationJson][0]
        self.assertEqual(content_type.content_type, MediaType.ApplicationJson)
        self.assertEqual(content_type.vendor, 'ficture.light')
        self.assertEqual(content_type.version, 1.0)
        self.assertEqual(MyHandler._CONS_MODEL[content_type], object)

    def test_consumes_decorator_with_model(self):

        @consumes(MediaType.ApplicationJson, object)
        class MyHandler(RequestHandler):

            def post(self):
                pass

        self.assertTrue(hasattr(MyHandler, '_CONS_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._CONS_CONTENT_TYPES), 1)
        self.assertTrue(MediaType.ApplicationJson in MyHandler._CONS_CONTENT_TYPES)
        content_type = MyHandler._CONS_CONTENT_TYPES[MediaType.ApplicationJson][0]
        self.assertEqual(content_type.content_type, MediaType.ApplicationJson)
        self.assertIsNone(content_type.vendor)
        self.assertIsNone(content_type.version)
        self.assertEqual(MyHandler._CONS_MODEL[content_type], object)


class TestProvidesDecorator(TestCase):
    '''Test the consumes decorator.'''

    @raises(AssertionError)
    def test_on_non_class(self):

        @provides(MediaType.ApplicationJson)
        def get():
            pass

    def test_simple_provides_decorator_with_post(self):

        @provides(MediaType.ApplicationJson)
        class MyHandler(RequestHandler):
            _PROD_CONTENT_TYPES = defaultdict(list)

            pass

        self.assertTrue(hasattr(MyHandler, '_PROD_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._PROD_CONTENT_TYPES), 1)
        self.assertTrue(MediaType.ApplicationJson in MyHandler._PROD_CONTENT_TYPES)
        content_type = MyHandler._PROD_CONTENT_TYPES[MediaType.ApplicationJson][0]
        self.assertEqual(content_type.content_type, MediaType.ApplicationJson)
        self.assertIsNone(content_type.vendor)
        self.assertIsNone(content_type.version)

    def test_provides_decorator_with_vendor_info(self):

        @provides(MediaType.ApplicationJson, 'ficture.light', version=1.0)
        class MyHandler(RequestHandler):

            def update_stuff(self):
                pass

        self.assertTrue(hasattr(MyHandler, '_PROD_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._PROD_CONTENT_TYPES), 1)
        self.assertTrue(MediaType.ApplicationJson in MyHandler._PROD_CONTENT_TYPES)
        content_type = MyHandler._PROD_CONTENT_TYPES[MediaType.ApplicationJson][0]
        self.assertEqual(content_type.content_type, MediaType.ApplicationJson)
        self.assertEqual(content_type.vendor, 'ficture.light')
        self.assertEqual(content_type.version, 1.0)

    def test_provides_decorator_with_model(self):

        @provides(MediaType.ApplicationJson)
        class MyHandler(RequestHandler):

            def update_stuff(self):
                pass

        self.assertTrue(hasattr(MyHandler, '_PROD_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._PROD_CONTENT_TYPES), 1)
        self.assertTrue(MediaType.ApplicationJson in MyHandler._PROD_CONTENT_TYPES)
        content_type = MyHandler._PROD_CONTENT_TYPES[MediaType.ApplicationJson][0]
        self.assertEqual(content_type.content_type, MediaType.ApplicationJson)
        self.assertIsNone(content_type.vendor)
        self.assertIsNone(content_type.version)


class SimpleMessage(Model):
    doc_id = StringType()
    message = StringType()


@provides(s.MediaType.ApplicationJson, default=True)
class MyHandler(RequestHandler):

    @s.async
    @s.cache(timedelta(minutes=10))
    def get(self, *args, **kwargs):
        raise s.Return(SimpleMessage(doc_id='test123', message='A test'))


@provides(s.MediaType.ApplicationJson, default=True)
class MyExtremeCachingHandler(RequestHandler):

    @s.async
    @s.cache(timedelta(minutes=10), s_max_age=timedelta(minutes=10),
             public=True, must_revalidate=True,
             proxy_revalidate=True)
    def get(self, *args, **kwargs):
        raise s.Return(SimpleMessage(doc_id='test123', message='A test'))


@provides(s.MediaType.ApplicationJson, default=True)
class MyPrivateCaching(RequestHandler):

    @s.async
    @s.cache(timedelta(seconds=10), s_max_age=timedelta(seconds=0),
             private=True, no_store=True)
    def get(self, *args, **kwargs):
        raise s.Return(SimpleMessage(doc_id='test123', message='A test'))

@provides(s.MediaType.ApplicationJson, default=True)
class CachingWithYielding(RequestHandler):

    @s.async
    @s.cache(timedelta(seconds=10))
    def get(self, *args, **kwargs):
        result = yield self.a_coroutine()
        assert result, 'yes'
        result = yield gen.Task(self.an_engine)
        assert result, 'yes again'
        raise s.Return(SimpleMessage(doc_id='test123', message='A test'))

    @gen.coroutine
    def a_coroutine(self):
        raise s.Return('yes')

    @gen.engine
    def an_engine(self, callback=None):
        callback('yes again')


class TestCacheDecorator(AsyncHTTPTestCase):

    def get_new_ioloop(self):
        return IOLoop.instance()

    def get_app(self):
        return Application([
            (r'/', MyHandler),
            (r'/cache', MyExtremeCachingHandler),
            (r'/private', MyPrivateCaching),
            (r'/nested_async', CachingWithYielding),
        ])

    def test_simple_timedelta(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertTrue('Cache-Control' in response.headers)
        self.assertEqual('max-age=600, must-revalidate',
                         response.headers['Cache-Control'])

    def test_extreme_cache(self):
        response = self.fetch('/cache')
        self.assertEqual(response.code, 200)
        self.assertTrue('Cache-Control' in response.headers)
        self.assertEqual('max-age=600, s-max-age=600, public, ' + \
                            'must-revalidate, proxy-revalidate',
                         response.headers['Cache-Control'])

    def test_private_cache(self):
        response = self.fetch('/private')
        self.assertEqual(response.code, 200)
        self.assertTrue('Cache-Control' in response.headers)
        self.assertEqual('max-age=10, private, no-store, must-revalidate',
                         response.headers['Cache-Control'])

    def test_caching_with_yielding(self):
        response = self.fetch('/nested_async')
        self.assertEqual(response.code, 200)
        self.assertTrue('Cache-Control' in response.headers)
        self.assertEqual('max-age=10, must-revalidate',
                         response.headers['Cache-Control'])
