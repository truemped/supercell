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

import logging.config
import os

import tornado.options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define

from supercell.api.environment import Environment


define('logconf', default='logging.cfg',
       help='Name of the logging configuration file')


define('port', default=8080, help='Port to listen on')


define('address', default='127.0.0.1', help='Address to bind on')


define('socketfd', default=None, help='Filedescriptor used from circus')


class Service(object):
    '''Main service implementation managing the `tornado.web.Application` and
    taking care of configuration.'''

    def main(self):
        '''Main method starting a `supercell` process.'''
        app = self.get_app()

        server = HTTPServer(app)

        if self.config.socketfd:
            import socket
            sock = socket.fromfd(int(self.config.socketfd), socket.AF_INET,
                                 socket.SOCK_STREAM)
            server.add_socket(sock)
        else:
            server.bind(self.config.port, address=self.config.address)
            server.start(1)

        self.slog.info('Starting supercell')
        IOLoop.instance().start()

    def get_app(self):
        '''Create the `tornado.web.Appliaction` instance and return it.'''
        # bootstrap the service
        self.bootstrap()

        # add handlers, health checks and others to the environment
        self.run()

        # do not allow any changes on managed objects anymore.
        self.environment.finalize_managed_objects()

        return self.environment.application(self.config)

    @property
    def slog(self):
        '''Initialize the logging and return the logger.'''
        if not hasattr(self, '_slog'):
            self._slog = self.initialize_logging()
        return self._slog

    @property
    def environment(self):
        '''The default environment instance.'''
        if not hasattr(self, '_environment'):
            self._environment = Environment()
        return self._environment

    @property
    def config(self):
        '''Assemble the configration files and command line arguments in order
        to finalize the service's configuration.'''
        if not hasattr(self, '_config'):
            # parse config files and command line arguments
            self.parse_config_files()
            self.parse_command_line()
            from tornado.options import options
            self._config = options
        return self._config

    def parse_config_files(self):
        '''Parse the config files and return the `config` object, i.e. the
        `tornado.options.options` instance.'''
        filename = self.environment.config_name
        for path in self.environment.config_file_paths:
            cfg = os.path.join(path, 'config.cfg')
            if os.path.exists(cfg):
                tornado.options.parse_config_file(cfg)

            cfg = os.path.join(path, filename)
            if os.path.exists(cfg):
                tornado.options.parse_config_file(cfg)

    def parse_command_line(self):
        '''Parse the command line arguments to set different configuration
        values.'''
        tornado.options.parse_command_line()

    def initialize_logging(self, name='supercell'):
        '''Initialize the python logging system.'''
        logging.config.fileConfig(self.config.logconf)
        slog = logging.getLogger(name)
        ts = self.environment.tornado_settings
        ts['log_function'] = self.environment.tornado_log_function(slog)
        return slog

    def bootstrap(self):
        '''Overide to change the environment.'''
        pass

    def run(self):
        '''Start the process and add the handlers and health checks to the
        environment.'''
        pass
