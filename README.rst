SuperCell
=========

SuperCell is a collection of best practices for creating with Tornado based
HTTP APIs. It resembles many ideas from Coda Hale's
`Dropwizard <http://dropwizard.codahale.com/>`_, a similar library
for JVM based HTTP APIs.


Example
=======

Code is worth more than words, so this is a simple example demonstrating the
idea::

    from tornado import options
    from tornado.gen import coroutine

    from supercell.api import produces, get, RequestHandler, MediaType, Service
    from supercell.healthcheck import HealthCheck, Healthy, Unhealthy
    from supercell.scales import Timed
    from supercell.schematics.models import Model
    from supercell.schematics.types import StringType, IntType


    options.define('defaultName', default='Your Name', type=str,
                   help='Default name shown when no name was given')


    options.define('template', default='templates/hello-world.txt', type=str,
                   help='Name for the hello world template')


    # model
    class Saying(Model):
        id = IntType()
        content = StringType()


    @produces(MediaType.APPLICATION_JSON)
    class SimpleExampleHandler(RequestHandler):

        @get
        @timed
        def returnResults(self):
            template = self.config['HELLO_WORLD_TEMPLATE']
            name = self.get_argument('name', self.config['DEFAULT_NAME'])
            yield Saying(id=12, content=template.render(name=name))


    class DummyHealthCheck(HealthCheck):

        @gen.coroutine
        def check(self):
            solrCheck = yield checkSolr()
            if not solrCheck.ok():
                yield Unhealthy(reason='Bad solr! Details: %s' % solrCheck)
            else:
                yield Healthy()


    class MyService(Service):
        
        def bootstrap(self, env):
            env.configFilePaths.append('./etc/')
            env.configFilePaths.append('/etc/myservice/')

        def run(self, conf, env):

            # add our handler
            self.add_handler('/hello-world', SimpleExampleHandler,
                             {'HELLO_WORLD_TEMPLATE': conf.template,
                              'DEFAULT_NAME': conf.defaultName},
                             name='hello-world')

            self.add_health_check(DummyHealthCheck)


    if __name__ == '__main__':
        MyService().main()


Configuration
=============

Configuration is managed via `Tornado options
<http://www.tornadoweb.org/en/stable/options.html>`_. In addition to setting
the options via command line, parsing config files is enabled as well. Config
files are named using a combination of user- and hostname. Running as user
'daniel' on host 'dev.local' would create a configfile named
'daniel\_dev.local.cfg'.

The resolution order is determined by the *Environment.configFilePaths*. In the
example above we have set this to ``./etc/`` and ``/etc/myservice/``. So when
starting the application the config files in the local directory is parsed
before the system administrator's config file. After that, command line
parameters are being parsed. So all config files are parsed in that order:

    ./etc/config
    ./etc/daniel_dev.local.cfg
    /etc/myservice/config
    /etc/myservice/daniel_dev.local.cfg

None of the files have to exist in order to start the application.

The default configuration of a *supercell* application contains several values
for communications such as ports for the main and the administrative interface
and may contain settings for the underlying *Tornado Application*.


Managed Objects
===============

Often you need some central instance to talk to other services to. In order to
simplify this, you can add a *ManagedObject* to the *Environment*, that you
then can retrieve in your handler implementation. Currently there is one
built-in version for handling ``AsynchronousHTTPClient`` instances. This will
use the ``PyCURL`` client, if available and fallback to the
``SimpleHTTPClient`` otherwise.

In order to add this to your environment you simply have to::

    def run(self, conf, env):
        from supercell.managed import AsyncHTTPClient
        env.add_managed_object('http_client', AsynchronousHttpClient)

In you handler code you may then get access to the client via the environment::

    ...
    client = env.get_managed_object('http_client')
    ...
