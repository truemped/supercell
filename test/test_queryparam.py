# vim: set fileencoding=utf-8 :
#
# Copyright (c) 2014 Daniel Truemper <truemped at googlemail.com>
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
from __future__ import (absolute_import, division, print_function,
                        with_statement)

import pytest

from schematics.models import Model
from schematics.types import StringType
from schematics.types import IntType

from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase

import supercell.api as s
from supercell.api import RequestHandler, provides
from supercell.environment import Environment
from supercell.queryparam import QueryParams, Param


class SimpleMessage(Model):
    doc_id = IntType()
    message = StringType()
    number = IntType()

    class Options:
        serialize_when_none = False


@provides(s.MediaType.ApplicationJson, default=True)
class MyQueryparamHandler(RequestHandler):

    @s.async
    @QueryParams((
        Param('docid', IntType(min_value=1, max_value=2, required=False)),
        Param('message', StringType(required=True))
    ))
    def get(self, *args, **kwargs):
        raise s.Return(SimpleMessage({"doc_id": kwargs.get('docid', 5),
                                      "message": kwargs.get('message')}))


@pytest.mark.onlyme
class TestSimpleQueryParam(AsyncHTTPTestCase):

    def get_app(self):
        env = Environment()
        env.add_handler('/test', MyQueryparamHandler)
        env.tornado_settings['debug'] = True
        return env.get_application()

    def get_new_ioloop(self):
        return IOLoop.instance()

    def test_simple_params(self):
        response = self.fetch('/test?docid=1&message=A%20test')

        self.assertEqual(200, response.code)
        self.assertEqual('{"message": "A test", "doc_id": 1}', response.body)

    def test_missing_required_param(self):
        response = self.fetch('/test?docid=1')

        self.assertEqual(400, response.code)
        self.assertEqual('{"msg": "Missing required argument ' +
                         '\\"message\\"", "error": true}', response.body)

    def test_bad_param_validation(self):
        response = self.fetch('/test?docid=noway&message=1')

        self.assertEqual(400, response.code)
        self.assertEqual('{"docid": ["Value is not int"], "error": true}',
                         response.body)
