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
'''Base mechanics for content type providers and a default provider for the
JSON (`application/json`) content type.
'''
from __future__ import absolute_import, division, print_function, with_statement

from collections import defaultdict
import json

from supercell._compat import with_metaclass, ifilter
from supercell.api import ContentType
from supercell.utils import parse_accept_header


__all__ = ['NoProviderFound', 'ProviderBase', 'JsonProvider']


class NoProviderFound(Exception):
    '''Raised if no matching provider for the client's `Accept` header was
    found.'''
    pass


class ProviderMeta(type):
    '''Meta class for all content type providers.

    This will simply register a provider with the respective content type
    information and make them available in a list of content types and their
    mappers.
    '''

    KNOWN_CONTENT_TYPES = defaultdict(list)

    def __new__(cls, name, bases, dct):
        provider_class = type.__new__(cls, name, bases, dct)

        ct = provider_class.CONTENT_TYPE
        if ct:
            ProviderMeta.KNOWN_CONTENT_TYPES[ct.content_type].append(
                    (ct, provider_class))
            if name == 'ProviderBase':
                provider_class.map_provider = ProviderMeta.map_provider

        return provider_class

    @staticmethod
    def map_provider(accept_header):
        '''Map a given content type to the correct provider implementation.

        If no provider matches, raise a `NoProviderFound` exception.

        TODO this algorithm can certainly be simplified via sorting and
        searching...
        '''
        accept_ctype = parse_accept_header(accept_header)
        if len(accept_ctype) == 0:
            raise NoProviderFound()

        # the list of accept content types is ordered by the client's q param
        # that will indicate the client's preferences.
        for (ctype, p, q) in accept_ctype:
            candidates = list(ifilter(
                lambda k: k[0].content_type == ctype,
                ProviderMeta.KNOWN_CONTENT_TYPES[ctype]))

            if len(candidates) == 0:
                # no toplevel provider found. Client wants `application/xml`
                # but we only have the default `application/json` provider for
                # example.
                continue

            if len(candidates) == 1:
                # we found only one matching provider, return it
                return candidates[0]

            if 'vendor' not in p:
                # no vendor information from the client, check if we have a
                # provider with only the content type
                candidates = list(ifilter(
                    lambda k: not k[0].vendor and not k[0].version,
                    candidates))

                if len(candidates) == 0:
                    continue

                if len(candidates) == 1:
                    return candidates[0][1]

                # no plain content type found, see if we can math another
                # accept header
                continue

            candidates = list(ifilter(
                lambda k: 'vnd.%s' % k[0].vendor == p['vendor'], candidates))

            if len(candidates) == 0:
                # no matching vendor information found.
                continue

            if len(candidates) == 1:
                return candidates[0][1]

            if 'version' not in p:
                # no version from the client, check if we have a provider with
                # only the content type and vendor information
                candidates = list(ifilter(
                    lambda k: not k[0].version, candidates))

                if len(candidates) == 0:
                    continue

                if len(candidates) == 1:
                    return candidates[0][1]

                continue

            candidates = list(ifilter(lambda k: k[0].version == p['version'],
                                      candidates))

            if len(candidates) == 0:
                # no matching vendor version found
                continue

            if len(candidates) == 1:
                return candidates[0][1]

        raise NoProviderFound()


class ProviderBase(with_metaclass(ProviderMeta, object)):
    '''Base class for content type providers.'''

    CONTENT_TYPE = None
    '''The target content type for the provider.'''

    def provide(self, model):
        '''This method should return the correct representation as a simple
        string (i.e. byte buffer) that will be used as return value.
        '''
        raise NotImplemented()


class JsonProvider(ProviderBase):
    '''Default `application/json` provider.'''

    CONTENT_TYPE = ContentType('application/json', None, None)

    def provide(self, model):
        '''Simply return the json via `json.dumps`.'''
        return json.dumps(model.serialize())
