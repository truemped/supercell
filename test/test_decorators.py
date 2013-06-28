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

import sys
if sys.version_info > (2, 7):
    from unittest import TestCase
else:
    from unittest2 import TestCase

from nose.tools import raises

from supercell.api import (RequestHandler, provides, consumes)


class TestConsumesDecorator(TestCase):
    '''Test the consumes decorator.'''

    @raises(AssertionError)
    def test_on_non_class(self):

        @consumes('application/json')
        def get():
            pass

    def test_simple_consumes_decorator_with_post(self):

        @consumes('application/json')
        class MyHandler(RequestHandler):

            _CONS_CONTENT_TYPES = defaultdict(list)

            def post(self):
                pass

        self.assertTrue(hasattr(MyHandler, '_CONS_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._CONS_CONTENT_TYPES), 1)
        self.assertTrue('application/json' in MyHandler._CONS_CONTENT_TYPES)
        content_type = MyHandler._CONS_CONTENT_TYPES['application/json'][0]
        self.assertEqual(content_type.content_type, 'application/json')
        self.assertIsNone(content_type.vendor)
        self.assertIsNone(content_type.version)
        self.assertIsNone(content_type.model)

    def test_consumes_decorator_with_vendor_info(self):

        @consumes('application/json', 'ficture.light', version=1.0)
        class MyHandler(RequestHandler):

            def post(self):
                pass

        self.assertTrue(hasattr(MyHandler, '_CONS_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._CONS_CONTENT_TYPES), 1)
        self.assertTrue('application/json' in MyHandler._CONS_CONTENT_TYPES)
        content_type = MyHandler._CONS_CONTENT_TYPES['application/json'][0]
        self.assertEqual(content_type.content_type, 'application/json')
        self.assertEqual(content_type.vendor, 'ficture.light')
        self.assertEqual(content_type.version, 1.0)
        self.assertIsNone(content_type.model)

    def test_consumes_decorator_with_model(self):

        @consumes('application/json', model=object)
        class MyHandler(RequestHandler):

            def post(self):
                pass

        self.assertTrue(hasattr(MyHandler, '_CONS_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._CONS_CONTENT_TYPES), 1)
        self.assertTrue('application/json' in MyHandler._CONS_CONTENT_TYPES)
        content_type = MyHandler._CONS_CONTENT_TYPES['application/json'][0]
        self.assertEqual(content_type.content_type, 'application/json')
        self.assertIsNone(content_type.vendor)
        self.assertIsNone(content_type.version)
        self.assertEqual(content_type.model, object)


class TestProvidesDecorator(TestCase):
    '''Test the consumes decorator.'''

    @raises(AssertionError)
    def test_on_non_class(self):

        @provides('application/json')
        def get():
            pass

    def test_simple_provides_decorator_with_post(self):

        @provides('application/json')
        class MyHandler(RequestHandler):
            _PROD_CONTENT_TYPES = defaultdict(list)

            pass

        self.assertTrue(hasattr(MyHandler, '_PROD_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._PROD_CONTENT_TYPES), 1)
        self.assertTrue('application/json' in MyHandler._PROD_CONTENT_TYPES)
        content_type = MyHandler._PROD_CONTENT_TYPES['application/json'][0]
        self.assertEqual(content_type.content_type, 'application/json')
        self.assertIsNone(content_type.vendor)
        self.assertIsNone(content_type.version)
        self.assertIsNone(content_type.model)

    def test_provides_decorator_with_vendor_info(self):

        @provides('application/json', 'ficture.light', version=1.0)
        class MyHandler(RequestHandler):

            def update_stuff(self):
                pass

        self.assertTrue(hasattr(MyHandler, '_PROD_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._PROD_CONTENT_TYPES), 1)
        self.assertTrue('application/json' in MyHandler._PROD_CONTENT_TYPES)
        content_type = MyHandler._PROD_CONTENT_TYPES['application/json'][0]
        self.assertEqual(content_type.content_type, 'application/json')
        self.assertEqual(content_type.vendor, 'ficture.light')
        self.assertEqual(content_type.version, 1.0)
        self.assertIsNone(content_type.model)

    def test_provides_decorator_with_model(self):

        @provides('application/json', model=object)
        class MyHandler(RequestHandler):

            def update_stuff(self):
                pass

        self.assertTrue(hasattr(MyHandler, '_PROD_CONTENT_TYPES'))
        self.assertEqual(len(MyHandler._PROD_CONTENT_TYPES), 1)
        self.assertTrue('application/json' in MyHandler._PROD_CONTENT_TYPES)
        content_type = MyHandler._PROD_CONTENT_TYPES['application/json'][0]
        self.assertEqual(content_type.content_type, 'application/json')
        self.assertIsNone(content_type.vendor)
        self.assertIsNone(content_type.version)
        self.assertEqual(content_type.model, object)
