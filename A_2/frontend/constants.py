import os, requests, json
resp = requests.get("http://169.254.169.254/latest/user-data")
config = json.loads(resp.content.decode('utf-8'))

# aws_config = {
#   'aws_access_key_id': config['aws_access_key_id'],
#   'awss_secret_access_key': config['aws_secret_access_key']
# }

db_config = {'user': config["MySQL_user"],
             'password': config["MySQL_password"],
             'host': config["MySQL_host"],
             'port': '3306',
             'database': 'memcache'
            }

IMAGE_FOLDER = os.path.dirname(os.path.abspath(__file__)) + 'main/frontend/static/images'