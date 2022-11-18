import os, requests, json
resp = requests.get("http://169.254.169.254/latest/user-data/")
conf_dict = json.loads(resp.content.decode('utf-8'))

db_config = {'user': 'admin',
             'password': 'ece1779group2',
             'host': 'briandatabase.cls58pggr43c.us-east-1.rds.amazonaws.com',
             'port': '3306',
             'database': 'briandatabase'}
             
# db_config = {'user': conf_dict["MYSQL_USER"],
#              'password': conf_dict["MYSQL_PASSWORD"],
#              'host': conf_dict["MYSQL_HOST"],
#              'port': '3306',
#              'database': 'briandatabase'}

max_capacity = 10
replacement_policy = 'Least Recently Used'
