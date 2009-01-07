#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Zine FastCGI Runner
    ~~~~~~~~~~~~~~~~~~~

    If FastCGI is your hosting environment this is the correct file.
    For working FastCGI support you have to have flup installed.

    For help on configuration have a look at the README file.

    :copyright: (c) 2009 by the Zine Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

# path to the instance. the folder for the instance must exist,
# if there is not instance information in that folder the websetup
# will show an assistent
INSTANCE_FOLDER = '/path/to/instance/folder'

# path to the Zine application code.
ZINE_LIB = '/usr/lib/zine'

# these values can be use to override database pool settings.
# see deployment guide for more details.
POOL_SIZE = None
POOL_RECYCLE = None
POOL_TIMEOUT = None

# if you are proxying into zine somehow (caching proxies or external
# fastcgi servers) set this value to True to enable proxy support.  Do
# not set this to True if you are not using proxies as this would be a
# security risk.
BEHIND_PROXY = None

# ----------------------------------------------------------------------------
# here you can further configure the fastcgi and wsgi app settings
# but usually you don't have to touch them.
import sys
sys.path.insert(0, ZINE_LIB)

from zine import get_wsgi_app, override_environ_config
from flup.server.fcgi import WSGIServer
override_environ_config(POOL_SIZE, POOL_RECYCLE, POOL_TIMEOUT, BEHIND_PROXY)
app = get_wsgi_app(INSTANCE_FOLDER)
srv = WSGIServer(app)

if __name__ == '__main__':
    srv.run()
