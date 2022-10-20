from memcache import webapp
import json

def response_builder(input=False):
    if input:
        response = webapp.response_class(
            response=json.dumps('OK'),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps('Bad Request'),
            status=400,
            mimetype='application/json'
        )
    return response