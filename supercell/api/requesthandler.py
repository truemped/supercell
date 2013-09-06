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

from datetime import datetime
from functools import partial
import json
import logging
import time

from schematics.models import Model
from tornado.escape import to_unicode
from tornado.util import bytes_type, unicode_type
from tornado.web import RequestHandler as rq, HTTPError

from supercell.api import MediaType
from supercell.api.cache import compute_cache_header
from supercell.api.metatypes import ReturnInformationT
from supercell.api.consumer import ConsumerBase, NoConsumerFound
from supercell.api.provider import ProviderBase, NoProviderFound


__all__ = ['RequestHandler']


_DEFAULT_CONTENT_TYPE = 'DEFAULT'


def _decode_utf8_and_latin1(value):
    '''Convert an string argument to a unicode string.

    Instead of decoding it as utf-8 we assume it is encoded as latin1.
    '''
    try:
        return to_unicode(value)
    except UnicodeDecodeError:
        if isinstance(value, (unicode_type, type(None))):
            return value
        assert isinstance(value, bytes_type), \
                'Expected bytes, unicode or None; got %s' % type(value)
        return value.decode('latin1')


class RequestHandler(rq):
    '''
    **supercell** request handler.

    The only difference to the :class:`tornado.web.RequestHandler` is an
    adopted :func:`RequestHandler._execute_method()` method that will handle
    the consuming and providing of request inputs and results.
    '''

    @property
    def environment(self):
        '''Convinience method for accessing the environment.'''
        return self.application.environment

    @property
    def config(self):
        '''Convinience method for accessing the environment.'''
        return self.application.config

    @property
    def logger(self):
        '''Use this property to write to the log files.

        In a request handler you would simply log messages like this::

            def get(self):
                self.logger.info('A test')
        '''
        if not hasattr(self, '_logger'):
            name = '%s:%s' % (self.__class__.__name__, self.request_id)
            self._logger = logging.getLogger(name)
        return self._logger

    def decode_argument(self, value, name=None):
        '''Overwrite the default :func:`RequestHandler.decode_argument()`
        method in order to allow *latin1* encoded URLs.
        '''
        return _decode_utf8_and_latin1(value)

    @property
    def request_id(self):
        '''Return a unique id per request. Collisions are allowed but should
        should not occur within a 10 minutes time window.

        The current implementation is based on a timestamp in milliseconds
        substracted by a large number to make the id smaller.
        '''
        if not hasattr(self, '_request_id'):
            self._request_id = int(time.time() * 1000) - 1374400000000
        return self._request_id

    def _request_summary(self):
        return self.request.method + " " + self.request.uri + \
            " (ip:" + self.request.remote_ip + ", r_id:" + \
            str(self.request_id) + ")"

    def _execute_method(self):
        '''Execute the request.

        The method to be executed is determined by the request method.
        '''
        if not self._finished:
            verb = self.request.method.lower()
            headers = self.request.headers
            method = getattr(self, verb)
            kwargs = self.path_kwargs

            if verb in ['post', 'put'] and 'Content-Type' in headers:
                # try to find a matching consumer
                try:
                    (model, consumer_class) = ConsumerBase.map_consumer(
                            headers['Content-Type'], self)
                    consumer = consumer_class()
                    kwargs['model'] = consumer.consume(self, model)
                except NoConsumerFound:
                    # TODO return available consumer types?!
                    raise HTTPError(406)

            if verb in ['get', 'head']:
                # check if there is caching information stored with the handler
                cache_config = self.environment.get_cache_info(self.__class__)
                if cache_config:
                    self.set_header('Cache-Control',
                                    compute_cache_header(cache_config))

                expires = self.environment.get_expires_info(self.__class__)
                if expires:
                    self.set_header('Expires', datetime.now() + expires)

            future_model = method(*self.path_args, **kwargs)
            if future_model:
                callback = partial(self._provide_result, verb, headers)
                future_model.add_done_callback(callback)

    def _provide_result(self, verb, headers, future_model):
        '''Find the correct provider for the result and call it with the final
        result.'''
        result = future_model.result()

        if isinstance(result, ReturnInformationT):
            self.set_header('Content-Type', MediaType.ApplicationJson)
            self.set_status(result.code)
            if 'additional' in result.message:
                self.logger.info(result.message['additional'])
            self.write(json.dumps(result.message))

        else:
            try:
                provider_class = ProviderBase.map_provider(
                        headers.get('Accept', ''), self, allow_default=True)
            except NoProviderFound:
                raise HTTPError(406)

            provider = provider_class()
            if isinstance(result, Model):
                provider.provide(future_model.result(), self)

        if not self._finished:
            self.finish()
