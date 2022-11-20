from flask import g
import mysql.connector
import os, requests, json
resp = requests.get("http://169.254.169.254/latest/user-data")
config = json.loads(resp.content.decode('utf-8'))

db_config = {'user': config["MySQL_user"],
             'password': config["MySQL_password"],
             'host': config["MySQL_host"],
             'port': '3306',
             'database': 'memcache'
            }

def connect_to_database():
    # connect to the database
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   port=db_config['port'],
                                   database=db_config['database'])

def get_db():
    # get the database
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db
    