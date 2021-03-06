0.7.0 - (August 24, 2015)
-------------------------

- Updated requires.io badge
- Removed buildout
- Tornado 4.2.1
- Python 3.4 compatibility


0.6.3 - (January 12, 2015)
--------------------------

- Add pytest to mocked sys.argv

0.6.2 - (December 28, 2014)
---------------------------

- Simplify integration testing of services

0.6.1 - (December 23, 2014)
---------------------------

- Optionally install signal handlers
- Fix: the exception is called NotImplementedError.
- Fix minor typo in @provides docstring

0.6.0 - (April 24, 2014)
------------------------

- add graceful shutdown
- allow logging to `stdout`
- Enable log file name with pid
- General base class for middleware decorators
- Typed query params deal with validation of query params

0.5.0 -
---------------------------

- add a NoContent (204) http response
- upgrade schematics to 0.9-4 (#7, #8)
- add a text/html provider for rendering html using tornado.template

0.4.0 - (December 09, 2013)
---------------------------

- Raise HTTPError when not returning a model
- A ValueError thrown by Model initialization returns a 400 Error
- fix for broken IE6 accept header
- allow latin1 encoded urls
- show-config, show-config-name and show-config-file-order
- enable tornado debug mode in the config
- Only add future callbacks if it is a future in the
  request handler
- Unittests using py.test
- HTTP Expires header support
- Caching configurable when adding the handlers
- Stats collecting using scales
- Fixed logging configuration

0.3.0 - (July, 16, 2013)
------------------------

- Introduce health checks into supercell
- Add a test for mapping ctypes with encodings

0.2.5 - (July 16, 2013)
-----------------------

- Only call finish() if the handler did not
- Minor fix for accessing the app in environments

0.2.4 - (July 10, 2013)
-----------------------

- Add the `@s.cache` decorator


0.2.3 - (July 4, 2013)
----------------------

- Allow binding to a socket via command line param
- Use MediaType.ApplicationJson instead of the plain string
- Add managed objects and their access in handlers


0.1.0 - (July 3, 2013)
----------------------

- Use the async decorator instead of gen.coroutine
- Application integration tests
- Initial base service with testing
- Add the initial default environment
- No Python 3.3 because schematics is not compatible
- Request handling code, working provider/consumer
- Base consumer and consumer mapping
- Cleaned up code for provider logic
- Working provider logic and accept negotiation
- Fixing FloatType on Python 3.3
- Initial provider logic
- PyPy testing, dependencies and py2.6 unittest2
- Decorators simplified and working correctly
- Unused import
- Fixing iteritems on dicts in Py 3.3
- Fixing sort comparator issue on Py 3.3
- fix string format in Python 2.6
- Fixing test requirements
- nosetests
- travis-ci
