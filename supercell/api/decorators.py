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
'''Several decorators for using with `supercell.api.RequestHandler`
implementations.

The decorators for mapping HTTP verbs to instance methods automatically add the
`tornado.web.asynchronous` and `tornado.gen.coroutine` decorators to the method,
so you don't have to.
'''
from __future__ import absolute_import, division, print_function, with_statement

from collections import defaultdict
from functools import wraps

from tornado import gen
from tornado.web import asynchronous

from supercell.api import ContentType, RequestHandler
from supercell._compat import ifilter
from supercell.utils import parse_accept_header


def async(fn):
    '''Decorator that only merges the `tornado.web.asynchronous` as well as the
    `tornado.gen.coroutine` decorators.

    Example::

        class MyHandler(RequestHandler):

            @async
            def get(self, user_id):
                # ...
                yield User()
    '''
    return asynchronous(gen.coroutine(fn))


def provides(content_type, vendor=None, version=None, model=None):
    '''Class decorator for mapping HTTP GET responses to content types and their
    representation.

    In order to allow the **application/json** content type, create the handler
    class like this::

        @provides('application/json')
        class MyHandler(RequestHandler):
            pass

    It is also possible to support more than one content type. The content type
    selection is then based on the client `Accept` header. If this is not
    present, ordering of the `provides` decorators matter, i.e. the first
    content type is used::

        @provides('application/json', model=MyModel)
        class MyHandler(RequestHandler):
            pass
    '''

    def wrapper(cls):
        '''The real class decorator.'''
        assert isinstance(cls, type), 'This decorator may only be used as ' + \
                'class decorator'

        if not hasattr(cls, '_PROD_CONTENT_TYPES'):
            cls._PROD_CONTENT_TYPES = defaultdict(list)

        cls._PROD_CONTENT_TYPES[content_type].append(ContentType(content_type,
                                                                 vendor,
                                                                 version,
                                                                 model))
        return cls

    return wrapper


def consumes(content_type, vendor=None, version=None, model=None):
    '''Class decorator for mapping HTTP POST and PUT bodies to

    Example::

        @consumes('application/json')
        class MyHandler(RequestHandler):

            @post
            def do_something_with_json(self, *args, **kwargs):
                # ...
                yield Response.OK
    '''

    def wrapper(cls):
        '''The real decorator.'''
        assert isinstance(cls, type), 'This decorator may only be used as ' + \
                'class decorator'
        if not hasattr(cls, '_CONS_CONTENT_TYPES'):
            cls._CONS_CONTENT_TYPES = defaultdict(list)

        cls._CONS_CONTENT_TYPES[content_type].append(ContentType(content_type,
                                                                 vendor,
                                                                 version,
                                                                 model))
        return cls
    return wrapper
