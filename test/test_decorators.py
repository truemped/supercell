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
from collections import defaultdict

from unittest import TestCase
from nose.tools import raises

from supercell.api import RequestHandler
from supercell.api.decorators import (get, put, post, delete, head, provides,
                                      consumes)


class TestSimpleHeader(TestCase):
    '''Test the simple HTTP verb decorators.'''

    def test_get_decorator(self):

        @get
        def sample_method():
            pass

        self.assertTrue(hasattr(sample_method, 'http_verb'))
        self.assertEqual(sample_method.http_verb, 'get')

    def test_put_decorator(self):

        @put
        def sample_method():
            pass

        self.assertTrue(hasattr(sample_method, 'http_verb'))
        self.assertEqual(sample_method.http_verb, 'put')

    def test_post_decorator(self):

        @post
        def sample_method():
            pass

        self.assertTrue(hasattr(sample_method, 'http_verb'))
        self.assertEqual(sample_method.http_verb, 'post')

    def test_delete_decorator(self):

        @delete
        def sample_method():
            pass

        self.assertTrue(hasattr(sample_method, 'http_verb'))
        self.assertEqual(sample_method.http_verb, 'delete')

    def test_head_decorator(self):

        @head
        def sample_method():
            pass

        self.assertTrue(hasattr(sample_method, 'http_verb'))
        self.assertEqual(sample_method.http_verb, 'head')


class TestConsumesDecorator(TestCase):
    '''Test the consumes decorator.'''

    def test_consumes_decorator(self):

        @consumes('application/json')
        def sample_method():
            pass

        self.assertTrue(hasattr(sample_method, 'consumes_content_type'))
        self.assertEqual(sample_method.consumes_content_type,
                         ('application/json', None))

    def test_consumes_decorator_with_vendor_info(self):

        @consumes('application/json', 'vnd.ficture.light-v1.0')
        def sample_method():
            pass

        self.assertTrue(hasattr(sample_method, 'consumes_content_type'))
        self.assertEqual(sample_method.consumes_content_type,
                         ('application/json', 'vnd.ficture.light-v1.0'))


class TestProvidesDecorator(TestCase):
    '''Test the provides class decorator.'''

    @raises(AssertionError)
    def test_provides_decorator_on_non_class(self):

        @provides('application/json')
        def sample_method():
            pass

    def test_provides_without_http_methods(self):

        @provides('application/json')
        class SampleHandler(RequestHandler):
            pass

        self.assertEqual(len(SampleHandler._METHODS), 0)

    def test_provides_with_get_method(self):

        @provides('application/json')
        class SampleHandler(RequestHandler):

            _METHODS = defaultdict(list)

            @get
            def sample_method(self):
                pass

        self.assertEqual(len(SampleHandler._METHODS), 1)
        method_details = SampleHandler._METHODS['get'][0]
        self.assertEqual(method_details[0], 'application/json')
        self.assertEqual(method_details[1], None)
        self.assertTrue(callable(method_details[2]))

    def test_provides_with_vendor(self):

        @provides('application/json', vendor_info='vnd.ficture-v1.3')
        class SampleHandler(RequestHandler):

            @get
            def sample_method(self):
                pass

            def test(self):
                pass

        self.assertEqual(len(SampleHandler._METHODS), 1)
        method_details = SampleHandler._METHODS['get'][0]
        self.assertEqual(method_details[0], 'application/json')
        self.assertEqual(method_details[1], 'vnd.ficture-v1.3')
        self.assertTrue(callable(method_details[2]))
