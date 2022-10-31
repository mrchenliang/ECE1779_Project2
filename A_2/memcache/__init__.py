from flask import Flask, current_app
import mysql.connector
import threading
from datetime import datetime
from backend.constants import db_config

webapp = Flask(__name__)

global memcache  # memcache
global memcache_stat  # statistic of the memcache
global memcache_config  # configuration of the memcache

memcache = {}  # memcache format:
# {
#   'key': {
#     'file': encoded base64 file, 
#     'size': file size in Byte, 
#     'timestamp': timestamp
#   }
# }

memcache_stat = {}  # memcache_stat format:
# {
#   'key_count': total count of key in cache,
#   'size_count': total count of file size,
#   'request_count': total request count,
#   'miss_count': total miss request count,
#   'hit_count': total hit request count,
#   'miss_rate': miss request rate,
#   'hit_rate': hit request rate
# }

memcache_config = {}  # memcache_config format
# {
#   'capacity': capacity of memcache in MB,
#   'replace_policy': replacement policy of memcache
# }

# initialize the memcache_stat
memcache_stat['key_count'] = 0
memcache_stat['size_count'] = 0
memcache_stat['request_count'] = 0
memcache_stat['miss_count'] = 0
memcache_stat['hit_count'] = 0
memcache_stat['miss_rate'] = 0
memcache_stat['hit_rate'] = 0

# initialize the memcache_config
memcache_config['max_capacity'] = 10
memcache_config['replacement_policy'] = 'Least Recently Used'

event = threading.Event()
lock = threading.Lock()
def background_job(db_config):
    print("Background Job Start")

    while True:
        event.wait(5)
        # Get the statistics from memcache_stat
        size_count = memcache_stat['size_count']
        key_count = memcache_stat['key_count']
        request_count = memcache_stat['request_count']
        miss_count = memcache_stat['miss_count']
        hit_count = memcache_stat['hit_count']
        # Connect to the database
        cnx = mysql.connector.connect(
            user=db_config['user'], 
            password=db_config['password'], 
            host=db_config['host'], 
            database=db_config['database'])            
        # Execute the query
        query = '''INSERT INTO cache_stats (cache_size, key_count, request_count, hit_count, miss_count) VALUES (%s, %s, %s, %s, %s)'''
        cnx.autocommit = False
        cursor = cnx.cursor(buffered=True)
        with lock:
            if threading.active_count() > 1:
                print("Memcache Replacement Policy: ", memcache_config['replacement_policy'])
                cursor.execute(query, (size_count, key_count, request_count, hit_count, miss_count))
                cnx.commit()
                print("------Memcache statistics store success------")
        cnx.close()
    print("Exit Background Job")
    return "success" 

print("main thread native_id:", threading.get_native_id())
threading.Thread(target=background_job, args= (db_config,)).start()

from memcache import main
