#!../venv/bin/python
from memcache_app import webapp
webapp.run('0.0.0.0',5000,debug=True,threaded=True)
