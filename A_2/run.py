#!../venv/bin/python
from frontend import webapp
webapp.run('0.0.0.0',5000,debug=True,threaded=True)
