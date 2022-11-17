#!../venv/bin/python
from memcache import webapp
webapp.run('0.0.0.0',5000,debug=True,threaded=True)
