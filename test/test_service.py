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

import mock
import pytest

from schematics.models import Model
from schematics.types import StringType
from tornado.ioloop import IOLoop
import tornado.options
from tornado.testing import AsyncHTTPTestCase

import supercell.api as s
from supercell.api.environment import Environment


class SimpleModel(Model):
    msg = StringType()


@s.provides(s.MediaType.ApplicationJson)
@s.consumes(s.MediaType.ApplicationJson, SimpleModel)
class MyHandler(s.RequestHandler):

    @s.async
    def get(self):
        self.logger.info('Holy moly')
        self.logger.info('That worked')
        raise s.Return(SimpleModel(msg='Holy moly'))

    @s.async
    def post(self, doc_id, model=None):
        self.logger.info('Holy moly')
        raise s.Return(SimpleModel(msg='Holy moly'))
        assert isinstance(self.environment, Environment)
        assert isinstance(self.config, tornado.options.options)
        raise s.OkCreated({'docid': 123})


@s.provides(s.MediaType.ApplicationJson, default=True)
class MyHandlerThrowingExceptions(s.RequestHandler):

    @s.async
    def get(self):
        self.logger.info('Starting request with unhandled exception')
        raise Exception()


class MyService(s.Service):

    def bootstrap(self):
        self.environment.config_file_paths.append('test/')

    def run(self):
        self.environment.add_handler('/test', MyHandler, {})
        self.environment.add_handler('/test/(\d+)', MyHandler, {})
        self.environment.add_handler('/exception', MyHandlerThrowingExceptions,
                                     {})


class ServiceTest(TestCase):

    @pytest.fixture(autouse=True)
    def empty_commandline(self, monkeypatch):
        monkeypatch.setattr(sys, 'argv', [])

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

    @mock.patch('tornado.ioloop.IOLoop.instance')
    def test_main_method(self, ioloop_instance_mock):
        service = MyService()
        service.main()

        self.assertEqual(len(ioloop_instance_mock.mock_calls), 4)


class ApplicationIntegrationTest(AsyncHTTPTestCase):

    def get_new_ioloop(self):
        return IOLoop.instance()

    def get_app(self):
        service = MyService()
        service.initialize_logging()
        return service.get_app()

    def test_simple_get(self):
        response = self.fetch('/test', headers={'Accept': s.MediaType.ApplicationJson})
        self.assertEqual(200, response.code)
        self.assertEqual('{"msg": "Holy moly"}', response.body)

    def test_get_with_exception(self):
        response = self.fetch('/exception')
        self.assertEqual(500, response.code)
