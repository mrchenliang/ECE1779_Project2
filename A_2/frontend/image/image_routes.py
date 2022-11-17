from flask import Blueprint, jsonify, render_template, request, send_file, redirect
from frontend.database_helper import get_db
from frontend.image.image_helper import *
import requests, json

image_routes = Blueprint('image_routes', __name__)

# Backend Host Port
backend_host = 'http://localhost:5002'

@image_routes.route('/upload_image', methods = ['GET','POST'])
# returns the upload page
def upload_image():
    if request.method == 'POST':
        key = request.form.get('key')
        # process the upload image request and add the image to the database
        status = process_image(request, key)
        return render_template('upload_image.html', status=status)
    return render_template('upload_image.html')

@image_routes.route('/get_image/<string:image>')
# returns the actual image
def get_image(image):
    filepath = 'static/images/' + image
    return send_file(filepath)

# TODO /images

@image_routes.route('/image', methods = ['GET','POST'])
# returns the view image page
def image():
    global memcache_host
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

@image_routes.route('/show_image', methods = ['GET','POST'])
def show_image():
    global cache_host
    if request.method == 'POST':
        key = request.form.get('key')
        jsonReq={"keyReq":key}
        # TODO: Add Memcache get
        ip_resp = requests.get(backend_app + '/hash_key', json=jsonReq)
        ip_dict = json.loads(ip_resp.content.decode('utf-8'))
        ip=ip_dict[1]
        res= requests.post('http://'+ str(ip) + ':5000/get', json=jsonReq)
        #res = None
        if(res == None or res.text=='Unknown key'):
            #get from db and update memcache
            cnx = get_db()
            cursor = cnx.cursor(buffered=True)
            query = "SELECT image_tag FROM image_table where image_key= %s"
            cursor.execute(query, (key,))
            if(cursor._rowcount):# if key exists in db
                image_tag=str(cursor.fetchone()[0]) #cursor[0] is the imagetag recieved from the db
                #close the db connection
                cnx.close()
                #put into memcache
                image=download_image(image_tag)
                jsonReq = {key:image}
                # TODO: Add to Cache
                res = requests.post('http://'+ str(ip) + ':5000/put', json=jsonReq)
                return render_template('show_image.html', exists=True, filename=image)
            else:#the key is not found in the db
                return render_template('show_image.html', exists=False, filename="does not exist")

        else:
            return render_template('show_image.html', exists=True, filename=res.text)
    return render_template('show_image.html')

@image_routes.route('/keys_list', methods=['GET'])
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
    if keys:
      return render_template('keys_list.html', keys=keys, length=len(keys))
    else:
      return render_template('keys_list.html')

@image_routes.route('/settings')
def settings():
	hostname = request.headers.get('Host').split(':')[0]
	print(hostname)
	return redirect('http://'+hostname + ':5001')
