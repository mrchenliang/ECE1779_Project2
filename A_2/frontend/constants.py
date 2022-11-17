import os, requests, json
resp = requests.get("http://169.254.169.254/latest/user-data/")
config = json.loads(resp.content.decode('utf-8'))

db_config = {'user': 'admin',
             'password': 'ece1779group2',
             'host': 'briandatabase.cls58pggr43c.us-east-1.rds.amazonaws.com',
             'port': '3306',
             'database': 'briandatabase'}
             
# db_config = {'user': config["MYSQL_USER"],
#              'password': config["MYSQL_PASSWORD"],
#              'host': config["MYSQL_HOST"],
#              'port': '3306',
#              'database': 'briandatabase'}


max_capacity = 10
replacement_policy = 'Least Recently Used'

aws_config = {
  'aws_access_key_id': config['aws_access_key_id'],
  'awss_secret_access_key': config['aws_secret_access_key']
}

IMAGE_FOLDER = os.path.dirname(os.path.abspath(__file__)) + 'main/frontend/static/images'