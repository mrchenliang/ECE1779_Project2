from flask import Blueprint, jsonify, request
from frontend.database_helper import get_db
from frontend.image.image_helper import *
import requests

api_routes = Blueprint('api_routes', __name__)

# Backend Host Port
backend_host = 'http://localhost:5002'

# Memcache host port
memcache_host = 'http://localhost:5001'

@api_routes.route('/api/list_keys', methods=['POST'])
# api end point to get a list of keys
def list_keys():
    try:
        # queries the database images for a list of keys
        cnx = get_db()
        cursor = cnx.cursor()
        query = 'SELECT images.key FROM images'
        cursor.execute(query)
        keys = []
        for key in cursor:
            keys.append(key[0])
        cnx.close()

        response = {
          'success': 'true',
          'keys': keys
        }
        return jsonify(response)

    except Exception as e:
        error_response = {
            'success': 'false',
            'error': {
                'code': '500 Internal Server Error',
                'message': 'Unable to fetch a list of keys, something went wrong.' + e
                }
            }
        return(jsonify(error_response))

@api_routes.route('/api/key/<string:key_value>', methods=['POST'])
# api end point to get the image of a specified key
def key(key_value):
    try:        
        request_json = {
            'key': key_value
        }
        # get the image by key from the memcache
        res = requests.post(memcache_host + '/get_from_memcache', json=request_json)
        # if the image is not by the key in the memcache
        if res.text == 'Key Not Found':
            # queries the database images by specific key
            cnx = get_db()
            cursor = cnx.cursor(buffered=True)
            query = 'SELECT images.location FROM images where images.key = %s'
            cursor.execute(query, (key_value,))
            # if the image is found
            if cursor._rowcount:
                location=str(cursor.fetchone()[0]) 
                cnx.close()
                # convert the image to Base64
                base64_image = convert_image_base64(location)
                request_json = { 
                    key_value: base64_image 
                }
                # put the key and image into the memcache
                res = requests.post(memcache_host + '/put_into_memcache', json=request_json)
                response = {
                    'success': 'true' , 
                    'content': base64_image
                }
                return jsonify(response)
            else:
                response = {
                    'success': 'false', 
                    'error': {
                        'code': '406 Not Acceptable', 
                        'message': 'The associated key does not exist'
                        }
                    }
                return jsonify(response)
        else:
            response = {
                'success': 'true' , 
                'content': res.text
            }   
            return jsonify(response)
    except Exception as e:
        error_response = {
            'success': 'false',
            'error': {
                'code': '500 Internal Server Error', 
                'message': 'Unable to fetch the associated key, something went wrong.' + e
                }
            }
        return(jsonify(error_response))

@api_routes.route('/api/upload', methods = ['POST'])
# api end point to put the key and image
def upload():
    try:
        key = request.form.get('key')
        # add the image to the database
        status = add_image(request, key)
        if status == 'INVALID' or status == 'FAILURE':
            error_response = {
                'success': 'false', 
                'error' : {
                    'code': '500 Internal Server Error', 
                    'message': 'Unable to upload image, something went wrong.'
                }
            }
            return jsonify(error_response)
        response = {
            'success': 'true'
        }
        return jsonify(response)

    except Exception as e:
        error_response = {
            'success': 'false',
            'error': {
                'code': '500 Internal Server Error', 
                'message': 'Unable to upload image something went wrong.' + e
                }
            }
        return(jsonify(error_response))
