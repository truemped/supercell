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
from tornado.web import RequestHandler as rq


__all__ = ['RequestHandler']


_DEFAULT_CONTENT_TYPE = 'DEFAULT'


class RequestHandler(rq):
    '''
    Supercell request handler.
    '''

    def initialize(self, conf, env):
        '''
        Each request handler as access to the configuration and environment
        '''
        self._conf = conf
        self._env = env

    def _execute_method(self):
        '''
        Execute the request.

        The method to be executed is determined by the request method.
        '''
