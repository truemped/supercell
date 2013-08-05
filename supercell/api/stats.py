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

from functools import wraps
import time

from greplin import scales
from greplin.scales.meter import MeterStat


def latency(fn):
    '''Measure execution latency of a certain request method.

    In order to measure latency for GET requests of a request handler you
    simply have to add the :func:`latency` decorator to the declaration::

        @s.latency
        @s.async
        def get(self, *args, **kwargs):
            ...

    The latency is recorded along the request path, i.e. if the request handler
    is defined like this::

        env.add_handler('/test/this', LatencyExample)

    the latency of GET/POST/PUT etc methods are stored with the path. In order
    to access the stats you may call **/_system/stats/test/this** or
    **/_system/stats/test**, e.g.
    '''

    @wraps(fn)
    def wrapper(self, *args, **kwargs):

        if not hasattr(self.__class__, '_stats_latency'):
            self.__class__._stats_latency = scales.NamedPmfDictStat('latency')

        original_on_finish = self.on_finish
        def latency_on_finish(*args, **kwargs):
            latency = time.time() - start
            self._stats_latency[self.request.method].addValue(latency)
            original_on_finish(*args, **kwargs)

        self.on_finish = latency_on_finish

        scales.init(self, self.request.path)
        start = time.time()
        return fn(self, *args, **kwargs)

    return wrapper


def metered(fn):
    '''Meter the execution of certain requests.

    The :func:`metered` stats will measure the 1/5/15 minutes averages for
    requests. This is also applied trivially::

        @s.metered
        @s.async
        def get(self, *args, **kwargs):
            ...

    As with the :func:`latency` stats, the :func:`metered` stats are recorded
    along the request path, i.e. you can get the stats values using the
    **/_system/stats/** route.
    '''

    @wraps(fn)
    def wrapper(self, *args, **kwargs):

        if not hasattr(self.__class__, '_stats_metered'):
            self.__class__._stats_metered = MeterStat(self.request.method)

        scales.init(self, self.request.path)
        self._stats_metered.mark()

        return fn(self, *args, **kwargs)

    return wrapper
