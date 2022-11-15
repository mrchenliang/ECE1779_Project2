import datetime, requests
from flask import Flask, render_template, url_for, request, send_file, json, jsonify, g
from frontend.cache_helper import get_cache, set_cache
from frontend.database_helper import get_db
from frontend.constants import max_capacity, replacement_policy, memcache_host
from frontend.image_helper import convert_image_base64, process_image, add_image
from frontend.graph_helper import prepare_graph, plot_graph
from frontend import webapp

@webapp.before_first_request
# initialize the cache configuration settings on first startup
def set_cache_config_settings():
    set_cache(max_capacity, replacement_policy)

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
    return render_template('main.html')

@webapp.route('/keys_list', methods=['GET'])
# returns the webpage list of keys page
def keys_list():
    # queries the database images for a list of keys
    cnx = get_db()
    cursor = cnx.cursor(buffered=True)
    query = 'SELECT images.key FROM images'
    cursor.execute(query)
    keys = []
    for key in cursor:
        keys.append(key[0])
    cnx.close()
    # returns the webpage list of keys page
    return render_template('keys_list.html', keys=keys, length=len(keys) )

@webapp.route('/get_image/<string:image>')
# returns the actual image
def get_image(image):
    filepath = 'static/images/' + image
    return send_file(filepath)

@webapp.route('/image', methods = ['GET','POST'])
# returns the view image page
def image():
    if request.method == 'POST':
        key_value = request.form.get('key_value')
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
                # returns view image page
                return render_template('image.html', exists=True, image=base64_image)
            else:
                return render_template('image.html', exists=False, image='does not exist')
        else:
            # returns view image page
            return render_template('image.html', exists=True, image=res.text)
    return render_template('image.html')

@webapp.route('/upload_image', methods = ['GET','POST'])
# returns the upload page
def upload_image():
    if request.method == 'POST':
        key = request.form.get('key')
        # process the upload image request and add the image to the database
        status = process_image(request, key)
        return render_template('upload_image.html', status=status)
    return render_template('upload_image.html')

@webapp.route('/api/list_keys', methods=['POST'])
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

@webapp.route('/api/key/<string:key_value>', methods=['POST'])
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

@webapp.route('/api/upload', methods = ['POST'])
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

@webapp.errorhandler(404)
# returns the 404 page
def page_not_found(e):
    return render_template('404.html'), 404

@webapp.errorhandler(500)
# returns the 500 page
def internal_server_error(e):
    return render_template('500.html'), 500
