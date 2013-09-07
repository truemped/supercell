supercell
=========

SuperCell is a collection of best practices for creating with Tornado based
HTTP APIs. It resembles many ideas from Coda Hale's
`Dropwizard <http://dropwizard.codahale.com/>`_, a similar library
for JVM based HTTP APIs.

|TravisImage|_ |CoverAlls|_

.. |TravisImage| image:: https://travis-ci.org/truemped/supercell.png?branch=master
.. _TravisImage: https://travis-ci.org/truemped/supercell
.. |CoverAlls| image:: https://coveralls.io/repos/truemped/supercell/badge.png?branch=master
.. _CoverAlls: https://coveralls.io/r/truemped/supercell

Example
=======

Code is worth more than words, so this is a simple example demonstrating the
idea::

    from tornado import options
    from schematics.models import Model
    from schematics.types import StringType
    import supercell.api as s


    options.define('defaultName', default='Your Name', type=str,
                   help='Default name shown when no name was given')


    options.define('template', default='templates/hello-world.txt', type=str,
                   help='Name for the hello world template')


    # model
    class Saying(Model):
        id = IntType()
        content = StringType()


    @produces(s.MediaType.ApplicationJson)
    class SimpleExampleHandler(s.RequestHandler):

        @s.async
        def get(self):
            template = self.config['HELLO_WORLD_TEMPLATE']
            name = self.get_argument('name', self.config['DEFAULT_NAME'])
            raise s.Return(Saying(id=12, content=template.render(name=name)))


    class MyService(s.Service):
        
        def bootstrap(self):
            self.environment.configFilePaths.append('./etc/')
            self.environment.configFilePaths.append('/etc/myservice/')

        def run(self):

            # add our handler
            self.add_handler('/hello-world', SimpleExampleHandler,
                             {'HELLO_WORLD_TEMPLATE': self.config.template,
                              'DEFAULT_NAME': self.config.defaultName},
                             name='hello-world')

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

    def run(self):
        env.add_managed_object('http_client', AsynchHTTPClient)

In you handler code you may then get access to the client via the environment::

    ...
    client = self.environment.http_client
    ...


Caching
=======

A simple decorator allows for fine grained control of public and browser
caches. The basic idea is to::

    class MyHandler(s.RequestHandler):

        @s.async
        @s.cache(timedelta(minutes=10))
        def get(self):
            raise s.Ok()

This will allow all caches to store a local copy of your response and serve it
for 10 minutes. By default the `must_revalidate` option is set, so that a cache
may not serve a stale copy but revalidate it when it is expired. So in this
example the header is set to::

    Cache-Control: max-age=600, must-revalidate

For a detailed description of the available options see the `Caching
Tutorial <http://www.mnot.net/cache_docs/>` and the official `RFC2616, sec
14.9 <http://www.ietf.org/rfc/rfc2616.txt>`.

