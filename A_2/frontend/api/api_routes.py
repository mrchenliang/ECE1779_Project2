from flask import Blueprint, jsonify, request
from frontend.database_helper import get_db
from frontend.image.image_helper import download_image, save_image
import requests, json

api_routes = Blueprint('api_routes', __name__)

# Backend Host Port
backend_host = 'http://0.0.0.0:5002'

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
        response = requests.get(backend_host + '/hash_key', json=request_json)
        dictionary = json.loads(response.content.decode('utf-8'))
        ip=dictionary[1]
        # get the image by key from the memcache
        res = requests.post('http://' + str(ip) + ':5000/get_from_memcache', json=request_json)
        # if the image is not by the key in the memcache
        if res.text == 'Key Not Found' or res == None:
            # queries the database images by specific key
            cnx = get_db()
            cursor = cnx.cursor(buffered=True)
            query = 'SELECT images.key FROM images where images.key = %s'
            cursor.execute(query, (key_value,))
            # if the image is found
            if cursor._rowcount:
                cnx.close()
                # convert the image to Base64
                image = download_image(key_value)
                if image == 'Image Not Found in S3':
                    response = {
                        'success': 'false', 
                        'error': {
                            'code': '406 Not Acceptable', 
                            'message': 'The associated image with key does not exist'
                            }
                        }
                    return jsonify(response)
                request_json = { 
                    key_value: image 
                }
                # put the key and image into the memcache
                res = requests.post('http://'+ str(ip) + ':5000/put_into_memcache', json=request_json)
                response = {
                    'success': 'true' , 
                    'content': image
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
        status = save_image(request, key)
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
