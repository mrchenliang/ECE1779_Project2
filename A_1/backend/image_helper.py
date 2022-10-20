import base64, os, requests
from backend import IMAGE_FOLDER
from backend.constants import ALLOWED_EXTENSIONS, memcache_host

from backend.database_helper import get_db

def convert_image_base64(fp):
    # convert the image to Base64
    with open(IMAGE_FOLDER + '/' + fp, 'rb') as image:
        base64_image = base64.b64encode(image.read())
    base64_image = base64_image.decode('utf-8')
    return base64_image

def process_image(request, key):
    # get the image file
    file = request.files['file']
    _, extension = os.path.splitext(file.filename)
    # if the image is one of the allowed extensions
    if extension.lower() in ALLOWED_EXTENSIONS:
        filename = key + extension
        # save the image in the local file system
        file.save(os.path.join(IMAGE_FOLDER, filename))
        request_json = {
            "key": key
        }
        # post request to invalidate memcache by key
        res = requests.post(memcache_host + '/invalidate_specific_key', json=request_json)
        # add the key and location to the database
        return add_image_to_db(key, filename)
    return 'INVALID'

def add_image_to_db(key, location):
    if key == '' or location == '':
        return 'FAILURE'
    try:
        # write to the database images with the key and location
        cnx = get_db()
        cursor = cnx.cursor(buffered = True)
        # check if the key already exists
        query_exists = 'SELECT EXISTS(SELECT 1 FROM images WHERE images.key = (%s))'
        cursor.execute(query_exists,(key,))
        # if it exists, delete the key and location
        for elem in cursor:
            if elem[0] == 1:
                query_delete = 'DELETE FROM images WHERE images.key=%s'
                cursor.execute(query_delete,(key,))
                break
        # write to the database images with the key and location
        query_insert = '''INSERT INTO images (images.key, images.location) VALUES (%s,%s);'''
        cursor.execute(query_insert,(key,location,))
        cnx.commit()
        cnx.close()
        return 'OK'
    except:
        return 'FAILURE'

def add_image(request, key):
    try:
        # get the image file
        file = request.files['file']
        _, extension = os.path.splitext(file.filename)
        # if the image is one of the allowed extensions
        if extension.lower() in ALLOWED_EXTENSIONS:
            filename = key + extension
            # save the image in the local file system
            file.save(os.path.join(IMAGE_FOLDER, filename))
            request_json = {
                "key": key
            }
            # post request to invalidate memcache by key
            res = requests.post(memcache_host + '/invalidate_specific_key', json=request_json)
            # add the key and location to the database
            return add_image_to_db(key, filename)
        return 'INVALID'
    except:
        return "INVALID"