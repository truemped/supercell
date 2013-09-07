.. vim: set fileencoding=UTF-8 :
.. vim: set tw=80 :


Logging
-------

Logging with `supercell` is configured with two simple configuration options:
the *logfile* defines the file to which the logs are written. By default it is
named *root.log* and does a daily log rotation for 10 days.

The second configuration sets the *loglevel*. This can be on of *DEBUG*, *INFO*,
*WARN*, *ERROR*, i.e. any valid default Python *logging.level* value.

The default logging implementation is simply adding a
*supercell.SupercellLoggingHandler* and sets the *loglevel* on the root logger.
We also disable the *tornado.log* module, so that it does not add its own
handler. The *SupercellLoggingHandler* is simply a *TimedRotatingFileHandler*
with some default values like number of backups and rotation interval and it
sets the logging format.

Custom logging
++++++++++++++

If the default logging does not fit your need, you may simply overwrite the
*initialize_logging* method of your *Service* implementation.
