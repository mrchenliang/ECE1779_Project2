from flask import render_template
from charts import webapp

@webapp.route('/')
@webapp.route('/home')
# returns the main page
def home():
    return render_template('main.html')