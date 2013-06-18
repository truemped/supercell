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





Example::

    class ThemenseitenTemplate(Model):
        id = IntType()
        template = StringType()
        name = StringType()

    class Themenseite(Model):
        id = IntType()
        title = StringType()
        templateId = IntType()


    class Render(Model):
        template = StringType()
        context = DictType()

    class ThemenseiteRender(Model):
        themenseite = ModelType(Themenseite)
        template = ModelType(ThemenseitenTemplate)
        docs = ListType(ModelType(SolrDoc))
        moduleA = ListType(ModelType(SolrDoc))
        moduleB = ListType(ModelType(SolrDoc))
        moduleC = ListType(ModelType(SolrDoc))


    class ThemeseitenCrud(Managed):

        @gen.coroutine
        def get_themenseite(self, url):
            themenseite = yield self.env.get_managed_object('dopplr').search(QUERY)

            if not themenseite:
                yield Result.NOT_FOUND
                return

            (template, docs, moduleA, moduleB, moduleC) = yield [
                self.dopplr.search(QUERY),
                self.dopplr.search(QUERY),
                self.dopplr.search(QUERY),
                self.dopplr.search(QUERY),
                self.dopplr.search(QUERY)]

            model = ThemenseiteRender(themenseite=themenseite,
                                      template=template,
                                      docs=docs
                                      moduleA=moduleA,
                                      moduleB=moduleB,
                                      moduleC=moduleC)

            yield model


    @produces(MediaType.TEXT_HTML)
    @produces(MediaType.APPLICATION_JSON, vendor='rtr-faz-themenseite')
    class ThemenseitenHandler(RequestHandler):

        @get
        @timed
        @cache(Timedelta(minutes=10))
        def computeThemenseite(self, url):
            crud = self.env.get_managed_object('THEMENSEITEN_CRUD')
            themenseite = yield crud.get_themenseite(url)
            yield themenseite


    class ThemenseitenProducer(Producer):

        def writer(self, model):
            self.render(template, model.to_dict())


    class ThemenseitenJsonProducer(Producer):
    
        vendor = 'rtr-faz-themenseite'
        show_type_vendor = False

        def writer(self, model):
            self.finish(model.to_json())


    class ThemenseitenService(Service):
    
        def run(self, conf, env):
            env.add_producer(MediaType.TEXT_HTML, ThemenseitenProducer)
            env.add_producer(MediaType.APPLICATION_JSON,
                ThemenseitenJsonProducer, vendor='rtr-faz-themenseite')

            env.add_managed_object('dopplr', dopplr.Client())
            env.add_managed_object('THEMENSEITEN_CRUD', ThemeseitenCrud)

            env.add_handler('/themenseite', ThemenseitenHandler)


    if __name__ == '__main__':
        ThemenseitenService().main()


    @consumes(MediaType.APPLICATION_JSON)
    @consumes(MediaType.APPLICATION_XML)
    class Indexer(RequestHandler):

        @post(ThemenseitenTemplate, validate=True)
        def storeTemplate(self, url, model=None):
            result = yield self.env.get_managed_object('dopplr').index(model)
            if result:
                yield Return.SUCCESS
            else:
                yield Return.ERROR


    class TemplateConsumer(Consumer):

        @gen.coroutine
        def read(self, request, model=None, validate=False):
            body = request.body
            parsed = lxml.parse(body)
            m = model()
            m.name = parsed.xpath('/sgjhrp')
            yield m

    
    ............


    ... Service) :

        def run(self, conf, env):
            ...
            env.add_consumer(MediaType.APPLICATION_XML, TemplateConsumer)
