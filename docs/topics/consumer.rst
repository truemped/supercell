.. vim: set fileencoding=UTF-8 :
.. vim: set tw=80 :


Consumer
--------

Consumers convert the client's input into an internal format defined as a
`schematics` model. The mapping of incoming data to one of the available
consumers is based on the client's `Content-Type` header. If this is missing and
no default consumer is defined, the client will receive a HTTP 406 error
(**Content not acceptable**).

Defining consumers for a request handler is done using the `consumes` decorator
on the class definition::

    @s.consumes(s.MediaType.ApplicationJson, model=Model)
    class MyHandler(s.RequestHandler):
        pass


Create custom consumer
^^^^^^^^^^^^^^^^^^^^^^

Creating a custom consumer is as easy as subclassing the `ConsumerBase` class.
See the `JsonConsumer` for example::

    class JsonConsumer(ConsumerBase):

        CONTENT_TYPE = ContentType('application/json')

        def consume(self, handler, model):
            return model(**json.loads(handler.request.body))


Content Types
^^^^^^^^^^^^^


The `CONTENT_TYPE` class level variable maps a certain `Content-Type` header to
this consumer. The `consume(handler, model)` method converts the request body to
an instance of the `model` class.

In situations where you need to accept the same content type, but the model has
different versions, you can use the `vendor` and `version` parameters to the
content type definition. This allows for multiple consumers for the same
serialization format like `json` but different versions of the data. See for
example the following two definitions and their respective content type value::

    ContentType('application/json') == 'application/json'

    ContentType('application/json', version='1.1', vendor='corp') == \
        'application/vnd.corp-v1.1+json'


If you create two consumers for both content types, the client can decide which
version is sent.
