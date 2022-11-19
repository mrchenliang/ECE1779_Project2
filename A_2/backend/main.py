from backend import webapp, memcache_pool
from flask import request
from backend import AWS_EC2_operator
from frontend.database_helper import get_db 
from backend.AWS_S3_operator import clear_images
import json, time, requests, threading
import hashlib

stat = ["Starting", "Stopping"]

pool_params = {
    'mode': 'manual',
}


def get_response(input=False):
    if input:
        response = webapp.response_class(
            response=json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps("Bad Request"),
            status=400,
            mimetype='application/json'
        )

    return response


def get_cache_response():
    cache_params = get_cache_params()
    response = webapp.response_class(
        response=json.dumps(cache_params),
        status=200,
        mimetype='application/json'
    )
    
    return response


def get_cache_params():
    """ Get the most recent cache configuration parameters
    from the database
    Return: cache_params row
    """
    try:
        cnx = get_db()
        cursor = cnx.cursor(buffered = True)
        query = '''SELECT * FROM cache_properties WHERE param_key = (SELECT MAX(param_key) FROM cache_properties LIMIT 1)'''
        cursor.execute(query)
        if(cursor._rowcount):# if key exists in db
            cache_params=cursor.fetchone()
            cache_dict = {
                'update_time': cache_params[3],
                'max_capacity': cache_params[1],
                'replacement_policy': cache_params[2]
            }
            return cache_dict
        return None
    except:
        return None


def node_states():
    """
    Using the function to pass the node status counts
    """
    stopping_nodes, starting_nodes, active_nodes = 0, 0, 0
    for _, ip in memcache_pool.items():
        if not ip == None:
            if ip == 'Stopping':
                stopping_nodes += 1
            elif ip == 'Starting':
                starting_nodes += 1
            else:
                active_nodes += 1
    message = {
        "active": active_nodes,
        "starting": starting_nodes,
        "stopping": stopping_nodes,
    }
    return message


def get_next_node():
    """ 
    Using the function to find the next available node to startup
    """
    global memcache_pool
    for id, ip in memcache_pool.items():
        if ip == None:
            return id
    return None


def get_active_node():
    """ 
    Using the function to find the active node
    """
    global memcache_pool
    for id, ip in reversed(memcache_pool.items()):
        if not ip == None and not ip == 'Stopping':
            return id
    return None


@webapp.route('/', methods=['GET', 'POST'])
def main():
    return get_response(True)


@webapp.route('/readyReq', methods=['GET', 'POST'])
def ready_request():
    global memcache_pool
    req_json = request.get_json(force=True)
    memcache_pool[req_json['instance_id']] = req_json['ip_address']
    print('New Memcache Host address:' + memcache_pool[req_json['instance_id']])
    notify = node_states()
    jsonReq={"message":notify}
    try:
        resp = requests.post("http://localhost:5000/show_notification", json=jsonReq)
    except:
        print("Frontend not started yet")
    return get_cache_response()


@webapp.route('/startInstance', methods=['GET', 'POST'])
def start_instance():
    instance_id = get_next_node()
    if not instance_id == None:
        print('Starting the instance ' + instance_id)
        memcache_pool[instance_id] = 'Starting'
        notify = node_states()
        jsonReq={"message":notify}
        try:
            resp = requests.post("http://localhost:5000/show_notification", json=jsonReq)
        except:
            print("Frontend not started yet")
        AWS_EC2_operator.start_instance(instance_id)

    return get_response(True)


@webapp.route('/stopInstance', methods=['GET', 'POST'])
def stop_instance():
    global memcache_pool
    instance_id = get_active_node()
    if not instance_id == None:
        print('Shutting down instance ' + instance_id)
        memcache_pool[instance_id] = 'Stopping'
        notify = node_states()
        jsonReq={"message":notify}
        try:
            resp = requests.post("http://localhost:5000/show_notification", json=jsonReq)
        except:
            print("Frontend not started yet")
        AWS_EC2_operator.shutdown_instance(instance_id)
    return get_response(True)


@webapp.route('/getCacheInfo', methods = ['GET', 'POST'])







