#!../venv/bin/python
from managerapp.main import webapp
webapp.run('0.0.0.0',5001,debug=True,threaded=True)
