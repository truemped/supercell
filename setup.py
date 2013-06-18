# vim: set fileencoding=utf-8 :
#
# Copyright (c) 2012 Daniel Truemper <truemped at googlemail.com>
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
import os
from imp import load_source
from setuptools import setup, find_packages


init = load_source('init', os.path.join('supercell', '__init__.py'))


tests_require = [
    'coverage',
    'tornado-pyvows>=0.5.0',
    'mock==1.0.1',
    ]


setup (
    name = 'supercell',
    version = '.'.join([str(v) for v in init.__version__]),

    author = 'Daniel Truemper',
    author_email = 'truemped@gmail.com',
    url = 'http://truemped.github.com/supercell',
    description = '',

    packages = find_packages(exclude=['vows']),

    install_requires = [
        'tornado >= 3.1.0',
    ],
    tests_require = tests_require,
    extras_require = {
        'test': tests_require,
        'futures': ['futures == 2.1.3'],
    }
)
