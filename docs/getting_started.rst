.. vim: set fileencoding=UTF-8 :
.. vim: set tw=80 :

Getting Started
===============
.. _getting_started:

This guide will help you get started with a simple *Hello World* Supercell
project.


Overview
--------

Supercell applications use `Tornado <https://github.com/facebook/tornado>`_ as a
HTTP server, `Schematics <https://github.com/j2labs/schematics/>`_ for dealing
with representations, and `Scales <https://github.com/Cue/scales>`_ for metrics.


Project structure
-----------------

A typical supercell application is structured in submodules:

- app

  - api - representations
  - core - domain implementation, i.e. crud operatios on representations
  - health - health checks
  - handler - request handler
  - provider - custom providers if any
  - consumer - custom consumers if any
  - service.py - the service class
  - config.py - the configuration


Configuration
-------------

Start with creating a `config.py` file::

    from tornado.options import define

    define('default_name', 'Hello %s', help='Default name')
    define('template', 'main.html', help='Tornado template file')

Here we are only defining the configuration names and their default
configuration values. Shortly we will se the different ways to really set the
configuraion.


Create a service class
----------------------

The service class is the part of the application defining it's handlers and
startup behaviour. For this purpose we start with a very simple class::

    import supercell.api as s

    class MyService(s.Service):

        def bootstrap(self):
            self.environment.config_file_paths.append('./etc')
            self.environment.config_file_paths.append('/etc/hello-world/')

        def run(self):
            # nothing done yet
            pass

    def main():
        MyService().main()

This class is not doing too much for now. Basically it only handles the order in
which configuration files are being parsed. Right now supercell will parse the
following files in that order:

#. $PWD/etc/config.cfg
#. $PWD/etc/$USER_$HOSTNAME.cfg
#. /etc/hello-world/config.cfg
#. /etc/hello-world/$USER_$HOSTNAME.cfg

After all these files were parsed, one may still overwrite the values using the
command line parameters.

Assume we have this entry point in the `setup.py`::

    hello-world = helloworld.service:main

we can start the application with something like `hello-world`. In order to
debug configuration settings you have the following command line parameters at
hand::

    # see the config file name you have to generate for this machine
    $ hello-world --show-config-name

    # see the order in which the files would be parsed
    $ hello-world --show-config-file-order

    # see the effective configuration
    $ hello-world --show-config


Representation
--------------

Now we create the model for the application::

    from schematics.models import Model
    from schematics.types import StringType, IntType

    class Saying(Model):

        id = IntType()
        content = StringType()

There is nothing special to it assuming you have some knowledge on schematics.
We simply have a `Saying` model that contains an `id` as integer and some
`content` as a string.


Request Handler
---------------

The request handler is very similar to a `Tornado` handler, except it also takes
care of de-/serializing in- and output::

    @s.produces(s.MediaType.ApplicationJson)
    class HelloWorld(s.RequestHandler):

        @property
        def counter(self):
            if not hasattr(self.__class__, '_counter'):
                self.__class__._counter = 0
            return self.__class__._counter or 0

        @counter.setter
        def counter(self, value):
            self.__class__._counter = value

        @s.async
        def get(self):
            self.counter += 1
            name = self.get_argument('name', self.config.default_name)
            content = self.render_string(self.config.template, name)
            raise s.Return(Saying(id=self.counter, content=content))

Ok, let's get through this example step by step. The `s.produces` decorator
tells supercell the content type, that this handler should return. In this case
a predefined one (`s.MediaType.ApplicationJson`) that will transform the
returned model as `application/json`.

The `counter` property is a simple wrapper around a class level variable that
stores the overall counter. Keep in mind that for each request a new instance of
the handler class is created, so a simple instance variable would always be `0`.

The `s.async` decorator is a simple wrapper for the two `Tornado` decorators
`web.asynchronous` and `gen.coroutine`. With the new `coroutine` decorator
`Tornado` can now make use of the `concurrent.Futures` of Python 3.3 and the
backported library for Python < 3.

Now we only have to add the request handler to the service implementation::

    class MyService(s.Service):

        def run(self):
            self.environment.add_handler('/hello-world', HelloWorld)


Start the application and point your browser to
`http://localhost:8080/hello-world <http://localhost:8080/hello-world>`_ to see
the response. The `id` is growing on every request and to change the output you
may add the `name` parameter: `http://localhost:8080/hello-world?name=you
<http://localhost:8080/hello-world?name=you>`_

See
`example/gettingstarted.py
<https://github.com/truemped/supercell/blob/master/example/gettingstarted.py>`_
for the full example code.
