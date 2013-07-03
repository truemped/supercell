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

import sys
if sys.version_info > (2, 7):
    from unittest import TestCase
else:
    from unittest2 import TestCase

from mock import patch
from schematics.models import Model
from schematics.types import StringType
from tornado import gen
from tornado.ioloop import IOLoop
import tornado.options
from tornado.testing import AsyncHTTPTestCase

import supercell.api as s
from supercell.api.environment import Environment


class SimpleModel(Model):
    msg = StringType()


@s.provides('application/json')
class MyHandler(s.RequestHandler):
    @gen.coroutine
    def get(self):
        raise s.Return(SimpleModel(msg='Holy moly'))


class MyService(s.Service):

    def bootstrap(self):
        self.environment.config_file_paths.append('test/')

    def run(self):
        self.environment.add_handler('/test', MyHandler, {})


class ServiceTest(TestCase):

    def test_environment_creation(self):
        service = s.Service()
        env = service.environment
        self.assertIsInstance(env, Environment)

    def test_parse_config_files(self):
        service = s.Service()
        env = service.environment
        env.config_file_paths.append('test/')
        tornado.options.define('test', default='default')
        service.parse_config_files()

        from tornado.options import options
        self.assertEqual('filevalue', options.test)

    def test_logging_initialization(self):
        service = s.Service()
        env = service.environment
        env.config_file_paths.append('test/')

        service.initialize_logging()

    @patch('tornado.ioloop.IOLoop.instance')
    def test_main_method(self, ioloop_instance_mock):
        service = MyService()
        service.main()

        self.assertEqual(len(ioloop_instance_mock.mock_calls), 4)


class ApplicationIntegrationTest(AsyncHTTPTestCase):

    def get_new_ioloop(self):
        return IOLoop.instance()

    def get_app(self):
        service = MyService()
        return service.get_app()

    def test_simple_get(self):
        response = self.fetch('/test', headers={'Accept': 'application/json'})
        self.assertEqual(200, response.code)
        self.assertEqual('{"msg": "Holy moly"}', response.body)
