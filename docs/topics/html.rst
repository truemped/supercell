.. vim: set fileencoding=UTF-8 :
.. vim: set tw=80 :


Rendering HTML
--------------

HTML is just another output format supported by `supercell`. The default
implementation is using tornado's built in template mechanism for rendering
HTML. A `RequestHandler` supporting HTML only has to implement the
`get_template()` method, that will return the template file name based on the
final model. By setting the `template_path` configuration variable one may
define the directory containing all templates.

A minimum example would look like this::

    @s.provides(s.MediaType.TextHtml, default=True)
    class SimpleHtml(s.RequestHandler):

        def get_template(self, model):
            return 'simple.html'

        def get(self, *args, **kwargs):
            raise s.Return(Saying(id=self.counter, content=content))

    class MyService(s.Service):

        def bootstrap(self):
            self.environment.tornado_settings['template_path'] = 'templates/'

        def run(self):
            self.environment.add_handler('/', SimpleHtml)
