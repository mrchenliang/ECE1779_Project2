import base64, os, requests, boto3, tempfile, json
from botocore.config import Config
from frontend.constants import IMAGE_FOLDER
# from frontend.image import s3_storage_helper
from frontend.database_helper import get_db


config = Config(
    region_name = 'us-east-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

# s3 = boto3.client('s3',config=config, aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])
s3 = boto3.client('s3',config=config)

backend_host = "http://0.0.0.0:5002"
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}

def download_image(key):
    try: 
        with open('Temp.txt', 'wb') as file:
            s3.download_fileobj('briansbucket', key, file)
        with open('Temp.txt', 'rb') as file:
            base64_image = file.read().decode('utf-8')
        file.close()
        os.remove("Temp.txt")
        return base64_image
    except:
        return 'Image Not Found in S3'

def convert_image_base64(fp):
    # convert the image to Base64
    with open(IMAGE_FOLDER + '/' + fp, 'rb') as image:
        base64_image = base64.b64encode(image.read())
    base64_image = base64_image.decode('utf-8')
    return base64_image

def process_image(request, key):
    global backend_host
    # get the image file
    file = request.files['file']
    _, extension = os.path.splitext(file.filename)
    # if the image is one of the allowed extensions
    if extension.lower() in ALLOWED_EXTENSIONS:
        filename = key + extension
        # save the image in the s3
        print('uploading')
        base64_image = base64.b64encode(file.read())
        s3.put_object(Body=base64_image, Key=key, Bucket='briansbucket', ContentType='image')
        print("uploaded")
        
        # post request to invalidate memcache by key
        request_json = {
            "key": key
        }
        resp = requests.get(backend_host + '/hash_key', json=request_json)
        dictionary = json.loads(resp.content.decode('utf-8'))
        ip=dictionary[1]
        res = requests.post('http://'+ str(ip) +':5000/invalidate_specific_key', json=request_json)
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

def save_image(request, key):
    global backend_host
    try:
        # get the image file
        file = request.files['file']
        _, extension = os.path.splitext(file.filename)
        # if the image is one of the allowed extensions
        if extension.lower() in ALLOWED_EXTENSIONS:
            filename = key + extension
            # save the image in the s3
            print("uploading")
            base64_image = base64.b64encode(file.read())
            s3.put_object(Body=base64_image, Key=key, Bucket='briansbucket', ContentType='image')
            print("uploaded")
            
            # post request to invalidate memcache by key
            request_json = {
                "key": key
            }
            resp = requests.get(backend_host + '/hash_key', json=request_json)
            dictionary = json.loads(resp.content.decode('utf-8'))
            ip=dictionary[1]
            res = requests.post('http://'+ str(ip) +':5000/invalidate_specific_key', json=request_json)
            # post request to invalidate memcache by key
            # add the key and location to the database
            return add_image_to_db(key, filename)
        return 'INVALID'
    except:
        return "INVALID"