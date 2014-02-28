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
'''Simple decorator for dealing with typed query parameters.'''
from __future__ import (absolute_import, division, print_function,
                        with_statement)

import functools

from schematics.exceptions import ConversionError, ValidationError

from supercell.api import Error


def QueryParams(params, kwargs_name='query'):
    """Simple decorator for ensuring types in query parameters.

    @QueryParams((
        ('limit', IntType()),
        ('q', StringType())
        )
    )
    """

    def wrapper(fn):

        @functools.wraps(fn)
        def _wrapper(s, *args, **kwargs):
            """Internal wrapper that will validate the desired query
            parameters using schematics types.

            :param s: the handler itself
            """

            kwargs[kwargs_name] = q = {}
            for (name, typedef) in params:
                if s.get_argument(name, None):
                    try:
                        parsed = typedef(s.get_argument(name))
                        q[name] = parsed
                    except (ConversionError, ValidationError) as e:
                        validation_errors = {name: e.messages}
                        raise Error(additional=validation_errors)
                elif typedef.required and not s.get_argument(name, None):
                    raise Error(additional={'msg':
                                            'Missing required argument "%s"' %
                                            name})

            return fn(s, *args, **kwargs)

        return _wrapper

    return wrapper
