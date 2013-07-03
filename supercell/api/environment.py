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
from collections import namedtuple

from tornado.web import Application as _TAPP


Handler = namedtuple('Handler', ['host_pattern', 'path', 'handler_class',
                                 'init_dict', 'name'])


class Application(_TAPP):
    '''Overwrite `tornado.web.Application` in order to give access to
    environment and configuration instances.'''

    def __init__(self, environment, config, **kwargs):
        '''Initialize the tornado Application and add the config and
        environment.
        '''
        self.environment = environment
        self.config = config
        super(Application, self).__init__(**kwargs)


class Environment(object):
    '''Base environment for `supercell` processes.'''

    def __init__(self):
        '''Initialize the handlers and health checks.'''
        self._handlers = []
        self._managed_objects = {}
        self._no_more_managed_objects = False

    def add_handler(self, path, handler_class, init_dict, name=None,
            host_pattern='.*$'):
        '''Add a handler to the tornado application.'''
        handler = Handler(host_pattern=host_pattern, path=path,
                          handler_class=handler_class, init_dict=init_dict,
                          name=name)
        self._handlers.append(handler)

    def add_managed_object(self, name, instance):
        '''Add a managed instance to the environment.

        You can access it later on from the environment as an attribute, so
        in your request handler you may::

            class MyHandler(s.RequestHandler):

                def get(self):
                    self.environment.managed
        '''
        assert name not in self._managed_objects
        assert not self._no_more_managed_objects
        self._managed_objects[name] = instance

    def finalize_managed_objects(self):
        '''When called it is not possible to add more managed objects.'''
        self._no_more_managed_objects = True

    def __getattr__(self, name):
        '''Retrieve a managed object from `self._managed_objects`.'''
        if name not in self._managed_objects:
            raise AttributeError('%s not a managed object' % name)
        return self._managed_objects[name]

    def add_health_check(self):
        # TODO
        pass

    @property
    def config_file_paths(self):
        '''The list containing all paths to look for config files.'''
        if not hasattr(self, '_config_file_paths'):
            self._config_file_paths = []
        return self._config_file_paths

    @property
    def tornado_settings(self):
        '''The dictionary passed to the `tornado.web.Application` containing
        all relevant tornado server settings.'''
        if not hasattr(self, '_tornado_settings'):
            self._tornado_settings = {}
        return self._tornado_settings

    def application(self, config):
        '''Create the tornado application and return it.'''
        if not hasattr(self, '_application'):
            self._application = Application(self, config,
                                            **self.tornado_settings)

        for handler in self._handlers:
            self._application.add_handlers(handler.host_pattern,
                                           [(handler.path,
                                            handler.handler_class,
                                            handler.init_dict)])
        return self._application

    @property
    def config_name(self):
        '''Determine the configuration file name for the machine this
        application is running on.'''
        if not hasattr(self, '_config_name'):
            import getpass
            import socket
            self._config_name = '%s_%s.cfg' % (getpass.getuser(),
                                               socket.gethostname())
        return self._config_name

    def tornado_log_function(self, logger):
        '''Return a function that will log tornado requests.'''
        if not hasattr(self, '_log_function'):

            def req_log(handler):
                if handler.get_status() < 400:
                    log_method = logger.info
                elif handler.get_status() < 500:
                    log_method = logger.warning
                else:
                    log_method = logger.error

                request_time = 1000.0 * handler.request.request_time()
                log_method("%d %s %.2fms", handler.get_status(),
                        handler._request_summary(), request_time)
            self._log_function = req_log

        return self._log_function
