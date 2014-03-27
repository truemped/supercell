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
from __future__ import (absolute_import, division, print_function,
                        with_statement)

import mock
import pytest
from tornado.options import define, options

from supercell.etcdconfig import is_enabled, EtcdConfig


define('etcdtest', type=str, default='test')
define('etcdtest_mock1', type=str, default='test')
define('etcdtest_mock2', type=str, default='test')


def test_enabled():
    assert is_enabled(), 'etcd should be loadable in tests'


@pytest.mark.integration
def test_config_parsing(etcd_client):

    key = '/supercell/tests/etcdtest'
    if key in etcd_client:
        etcd_client.delete(key)

    config = EtcdConfig('/supercell/tests')
    config.get_config()
    assert 'test' == options.etcdtest

    etcd_client.set(key, 'etcdvalue')

    config.get_config()
    assert 'etcdvalue' == options.etcdtest

    etcd_client.delete(key)


def test_mocked_config_parsing():

    key = '/supercell/tests/etcdtest_mock2'
    config = EtcdConfig('/supercell/tests')

    m = mock.MagicMock(name='etcd')
    m.configure_mock(**{
        'get.return_value.value': 'mock_test'
    })

    m.__contains__.side_effect = lambda x: x == key

    config._client = m
    config.get_config()
    assert 'test' == options.etcdtest_mock1
    assert 'mock_test' == options.etcdtest_mock2
