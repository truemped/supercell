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
"""A wrapper for etcd based configuration management.

etcd is a distributed configuration server similar to Zookeeper.
TODO: some more text... :)
"""

from tornado.options import options

try:
    import etcd
except ImportError:
    # cannot import etcd, so ignore it
    etcd = None


def is_enabled():
    return etcd is not None


class EtcdConfig(object):

    def __init__(self, prefix, **kwargs):
        """Initialize the etcd connection. All `kwargs` are passed to the
        `etcd.Client()` constructor.
        """
        assert etcd, 'etcd not importable!?'
        self._client = etcd.Client(**kwargs)
        self._prefix = prefix

    @property
    def prefix(self):
        return self._prefix

    def key(self, name):
        return '/'.join([self.prefix, name])

    def get_config(self):
        """Parse the current state of `tornado.options` definitions and try to
        find values for them in `etcd`.
        """
        for opt in options._options.itervalues():
            etcd_name = self.key(opt.name)
            if etcd_name in self._client:
                etcd_resp = self._client.get(self.key(opt.name))
                opt.parse(etcd_resp.value)
