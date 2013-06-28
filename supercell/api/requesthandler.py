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

from tornado.web import RequestHandler as rq, HTTPError

from supercell.utils import parse_accept_header
from supercell._compat import ifilter


__all__ = ['RequestHandler']


_DEFAULT_CONTENT_TYPE = 'DEFAULT'


class RequestHandler(rq):
    '''
    Supercell request handler.
    '''

    def __init__(self, *args, **kwargs):
        '''Initialize the request and map the instance methods to the HTTP
        verbs.'''
        super(RequestHandler, self).__init__(*args, **kwargs)

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
        if not self._finished:
            verb = self.request.method.lower()
            method = getattr(self, verb)
            self._when_complete(method(*self.path_args, **self.path_kwargs),
                                self._execute_function)

    def _content_type_negotiation(self):
        '''Negotiate the content types.'''
        if verb in ['get', 'head'] and 'Accept' in self.request.headers:
            # do the accept header parsing for GET requests only
            accepts = parse_accept_header(self.request.headers['Accept'])
            self._check_simple_content_type(accepts, verb)

        elif verb in ['post', 'put'] and 'Content-Type' in self.request.headers:
            ctype_header = self.request.headers['Content-Type']
            content_type = parse_accept_header(ctype_header)
            self._check_simple_content_type(content_type, verb)

        return method

    def _check_simple_content_type(self, content_types, verb):

        if len(content_types) > 0:
            for (ctype, p, q) in content_types:
                methods = list(ifilter(lambda k: k.content_type == ctype,
                                        self._METHODS[verb]))

                l = len(methods)
                if l == 0:
                    # TODO return allowed content types
                    raise HTTPError(406)
                elif l == 1:
                    method = methods[0]
                elif 'vendor' in p:
                    method = self._check_vendor_content_type(methods, p)

        return method

    def _check_vendor_content_type(self, methods, p):
        '''Execute the correct function based on the vendor content type or
        riase a 406 HTTP status.'''
        methods = list(ifilter(lambda k: k.vendor == p['vendor'], methods))
        l = len(methods)
        if l == 0:
            # TODO return allowed content types
            raise HTTPError(406)
        elif l == 1:
            return methods[0]
        elif 'version' in p:
            # still no luck, check if we have a correct version
            # added to the vendor info
            methods = ifilter(lambda k: k.version == p['version'])

            if len(methods) == 0:
                # TODO return allowed content types
                raise HTTPError(406)
            elif l == 1:
                return methods[0]
            # this means, that the client requested a vendor version that the
            # server does not support.
            raise HTTPError(406)
