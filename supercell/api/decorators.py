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
'''Several decorators for using with :class:`supercell.api.RequestHandler`
implementations.
'''
from __future__ import absolute_import, division, print_function, with_statement

from collections import defaultdict
from functools import wraps

from tornado import gen
from tornado.web import asynchronous

from supercell.api import ContentType


def async(fn):
    '''Decorator that merges the :func:`tornado.web.asynchronous` as well as
    the :func:`tornado.gen.coroutine` decorators.

    Example::

        class MyHandler(s.RequestHandler):

            @s.async
            def get(self, user_id):
                # ...
                raise s.Return(User())
    '''
    return asynchronous(gen.coroutine(fn))


def provides(content_type, vendor=None, version=None, default=False):
    '''Class decorator for mapping HTTP GET responses to content types and their
    representation.

    In order to allow the **application/json** content type, create the handler
    class like this::

        @s.provides(sMediaType.ApplicationJson)
        class MyHandler(sRequestHandler):
            pass

    It is also possible to support more than one content type. The content type
    selection is then based on the client **Accept** header. If this is not
    present, ordering of the :func:`provides` decorators matter, i.e. the first
    content type is used::

        @s.provides(s.MediaType.ApplicationJson, model=MyModel)
        class MyHandler(s.RequestHandler):
            ...

    :param str content_type: The base content type such as **application/json**
    :param model: The model that should be consumed.
    :type model: :class:`schematics.models.Model`
    :param str vendor: Any vendor information for the base content type
    :param float version: The vendor version
    :param bool default: If **True** and no **Accept** header is present, this
                         content type is provided
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

        @s.consumes(s.MediaType.ApplicationJson, model=Model)
        class MyHandler(s.RequestHandler):

            def post(self, *args, **kwargs):
                # ...
                raise s.OkCreated()

    :param str content_type: The base content type such as **application/json**
    :param model: The model that should be consumed.
    :type model: :class:`schematics.models.Model`
    :param str vendor: Any vendor information for the base content type
    :param float version: The vendor version
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


def cache(max_age, s_max_age=None, public=False, private=False, no_cache=False,
          no_store=False, must_revalidate=True, proxy_revalidate=False):
    '''Set the `Cache-Control` HTTP header to allow for fine grained caching
    controls.

    For detailed information read http://www.mnot.net/cache_docs/ and
    http://www.ietf.org/rfc/rfc2616.txt

    Usage::

        @cache(timedelta(minutes=10))
        def get(self):
            self.finish({'ok': True})

    This would allow public caches to store the result for 10 minutes.

    :param max_age: Number of seconds the response can be cached
    :type max_age: datetime.timedelta

    :param s_max_age: Like `max_age` but only applies to shared caches
    :type s_max_age: datetime.timedelta

    :param public: Marks responses as cachable even if they contain
                   authentication information
    :type public: bool

    :param private: Allows the browser to cache the result but not shared
                    caches
    :type private: bool

    :param no_cache: If *True* caches will revalidate the request before
                     delivering the cached copy
    :type no_cache: bool

    :param no_store: Caches should not store any cached copy.
    :type no_store: bool

    :param must_revalidate: Tells the cache to not serve stale copies of the
                            response
    :type must_revalidate: bool

    :param proxy_revalidate: Like `must_revalidate` except it only applies to
                             public caches
    :type proxy_revalidate: bool
    '''

    def wrapper(fn):

        @wraps(fn)
        def _func(self, *args, **kwargs):
            '''Inner method setting the HTTP header according to the params.'''
            params = []
            params.append('max-age=%s' % max_age.seconds)
            if s_max_age:
                params.append('s-max-age=%s' % s_max_age.seconds)
            if public:
                params.append('public')
            if private:
                params.append('private')
            if no_cache:
                params.append('no-cache')
            if no_store:
                params.append('no-store')
            if must_revalidate:
                params.append('must-revalidate')
            if proxy_revalidate:
                params.append('proxy-revalidate')

            self.set_header('Cache-Control', ', '.join(params))
            fn(self, *args, **kwargs)

        return _func
    return wrapper
