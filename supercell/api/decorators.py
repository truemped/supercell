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
from collections import defaultdict

from tornado import gen
from tornado.web import asynchronous

from supercell._compat import iteritems


def get(fn):
    '''Decorator for HTTP GET methods.

    Wrap any `supercell.api.RequestHandler` method with it in order to map the
    method with the incoming request.

    Example::

        class MyHandler(RequestHandler):

            @get
            def show_user(self, user_id):
                # ...
                yield User()
    '''
    fn.http_verb = 'get'
    return asynchronous(gen.coroutine(fn))


def put(fn):
    '''Decorator for HTTP PUT methods.

    Wrap any `supercell.api.RequestHandler` method with it in order to map the
    method to the incoming request.

    Example::

        class MyHandler(RequestHandler):

            @put
            def add_user(self, user_id):
                # ...
                yield Response.OK
    '''
    fn.http_verb = 'put'
    return asynchronous(gen.coroutine(fn))


def post(fn):
    '''Decorator for HTTP POST methods.

    Wrap any `supercell.api.RequestHandler` method with it in order to map the
    method with the incoming request.

    Example::

        class MyHandler(RequestHandler):

            @post
            def add_user(self):
                # ...
                yield Response.OK
    '''
    fn.http_verb = 'post'
    return asynchronous(gen.coroutine(fn))


def delete(fn):
    '''Decorator for HTTP DELETE methods.

    Wrap any `supercell.api.RequestHandler` method with it in order to map the
    method with the incoming request.

    Example::

        class MyHandler(RequestHandler):

            @delete
            def remove_user(self, user_id):
                # ...
                yield Response.OK
    '''
    fn.http_verb = 'delete'
    return asynchronous(gen.coroutine(fn))


def head(fn):
    '''Decorator for HTTP HEAD methods.

    Wrap any `supercell.api.RequestHandler` method with it in order to map the
    method with the incoming request.

    Example::

        class MyHandler(RequestHandler):

            @head
            def perform_head(self, *args, **kwargs):
                yield Response.OK
    '''
    fn.http_verb = 'head'
    return asynchronous(gen.coroutine(fn))


def provides(content_type, vendor_info=None):
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

        @provides('application/json')
        @provides('application/xml')
        class MyHandler(RequestHandler):
            pass
    '''

    def wrapper(cls):
        '''The real class decorator.'''
        assert isinstance(cls, type), 'This decorator may only be used as ' + \
                'class decorator'
        if not hasattr(cls, '_METHODS'):
            cls._METHODS = defaultdict(list)

        for name, method in iteritems(cls.__dict__):
            if hasattr(method, 'http_verb') and method.http_verb in ['get']:
                # only the GET method will create representations of something,
                # now add this method to cls._METHODS
                cls._METHODS['get'].append((content_type, vendor_info, method))
        return cls

    return wrapper


def consumes(content_type, vendor_info=None):
    '''Instaance method decorator allowing different implementations for HTTP
    methods to consume different input.

    Example::

        class MyHandler(RequestHandler):

            @post
            @consumes('application/json')
            def do_something_with_json(self, *args, **kwargs):
                # ...
                yield Response.OK
    '''

    def wrapper(fn):
        '''The real decorator.'''
        fn.consumes_content_type = (content_type, vendor_info)
        return fn

    return wrapper
