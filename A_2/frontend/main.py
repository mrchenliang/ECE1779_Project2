import datetime, requests
from glob import glob
from flask import Flask, render_template, g, request, redirect, url_for
from frontend.image import image_routes
from frontend.api import api_routes
import json

# Flask Blueprint Setup
webapp = Flask(__name__)
webapp.register_blueprint(image_routes)
webapp.register_blueprint(api_routes)

global pool_notification
pool_notification = ""

@webapp.teardown_appcontext
# close out the db connection on shutdown
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.route('/')
@webapp.route('/home')
# returns the main page
def home():
    global pool_notification
    return render_template('main.html', pool_notification=pool_notification)

@webapp.route("/show_notification", methods=['POST'])
def show_notification():
    global pool_notification
    pool_notification = request.get_json(force=True)
    response = webapp.response_class(
            status = 200,
            response = json.dumps("OK"),
            mimetype = 'application/json'
        )
    return response

@webapp.route("/clear_notification", methods=['POST'])
def clear_notification():
    global pool_notification
    pool_notification = ""
    return redirect(redirect_url())

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

@webapp.errorhandler(404)
# returns the 404 page
def page_not_found(e):
    return render_template('404.html'), 404

@webapp.errorhandler(500)
# returns the 500 page
def internal_server_error(e):
    return render_template('500.html'), 500
