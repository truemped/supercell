.. vim: set fileencoding=UTF-8 :
.. vim: set tw=80 :

Welcome to supercell's documentation!
=====================================

Supercell is a simple set of classes for creating domain driven RESTful APIs
in Python. We use `schematics` for domain modeling, `scales` for statistics and
`Tornado` as web server.

A very simple example for a supercell request handler looks like this::

    from schematics.models import Model
    from schematics.types import StringType, IntType

    class Saying(Model):

        id = IntType()
        content = StringType()

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


The **Getting Started** guide should help you becoming familiar with the
ideas behind and the **Topics** contain a growingly part of in depth
documentation on certain aspects. The **API** contains the full API
documentation.

Contents:
---------

.. toctree::
    :maxdepth: 2

    getting_started
    topics/index
    api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
