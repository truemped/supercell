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

from tornado import gen
from tornado.web import asynchronous

from supercell.api import ContentType


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


def provides(content_type, vendor=None, version=None, default=False):
    '''Class decorator for mapping HTTP GET responses to content types and their
    representation.

    In order to allow the **application/json** content type, create the handler
    class like this::

        @provides(MediaType.ApplicationJson)
        class MyHandler(RequestHandler):
            pass

    It is also possible to support more than one content type. The content type
    selection is then based on the client `Accept` header. If this is not
    present, ordering of the `provides` decorators matter, i.e. the first
    content type is used::

        @provides(MediaType.ApplicationJson, model=MyModel)
        class MyHandler(RequestHandler):
            pass
    '''

    def wrapper(cls):
        '''The real class decorator.'''
        assert isinstance(cls, type), 'This decorator may only be used as ' + \
                'class decorator'

        if not hasattr(cls, '_PROD_CONTENT_TYPES'):
            cls._PROD_CONTENT_TYPES = defaultdict(list)

        ctype = ContentType(content_type,
                            vendor,
                            version)
        cls._PROD_CONTENT_TYPES[content_type].append(ctype)
        if default:
            assert 'default' not in cls._PROD_CONTENT_TYPES, 'TODO: nice msg'
            cls._PROD_CONTENT_TYPES['default'] = ctype

        return cls

    return wrapper


def consumes(content_type, model, vendor=None, version=None):
    '''Class decorator for mapping HTTP POST and PUT bodies to

    Example::

        @consumes(MediaType.ApplicationJson, model=Model)
        class MyHandler(RequestHandler):

            @post
            def do_something_with_json(self, *args, **kwargs):
                # ...
                raise Ok()
    '''

    def wrapper(cls):
        '''The real decorator.'''
        assert isinstance(cls, type), 'This decorator may only be used as ' + \
                'class decorator'
        assert model, 'In order to consume content a schematics model ' + \
                'class has to be given via the model parameter'

        if not hasattr(cls, '_CONS_CONTENT_TYPES'):
            cls._CONS_CONTENT_TYPES = defaultdict(list)
        if not hasattr(cls, '_CONS_MODEL'):
            cls._CONS_MODEL = dict()

        ct = ContentType(content_type, vendor, version)
        cls._CONS_CONTENT_TYPES[content_type].append(ct)
        cls._CONS_MODEL[ct] = model
        return cls

    return wrapper
