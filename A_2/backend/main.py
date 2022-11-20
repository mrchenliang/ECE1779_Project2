from backend import webapp, memcache_pool
from flask import request
from backend import AWS_EC2_operator
from frontend.database_helper import get_db 
from backend.AWS_S3_operator import clear_images
import json, time, requests, threading
import hashlib
from backend.constants import max_capacity, replacement_policy

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
    cache_properties = get_memcache_properties()
    response = webapp.response_class(
        response=json.dumps(cache_properties),
        status=200,
        mimetype='application/json'
    )
    
    return response


def get_memcache_properties():
    """ Get the most recent cache configuration parameters
    from the database
    Return: cache_properties row
    """
    try:
        cnx = get_db()
        cursor = cnx.cursor(buffered = True)
        query = '''SELECT * FROM cache_properties WHERE id = (SELECT MAX(id) FROM cache_properties LIMIT 1)'''
        cursor.execute(query)
        if(cursor._rowcount):# if key exists in db
            cache_properties=cursor.fetchone()
            cache_dict = {
                'created_at': cache_properties[3],
                'max_capacity': cache_properties[1],
                'replacement_policy': cache_properties[2]
            }
            return cache_dict
        return {
            'created_at': time.time(),
            'max_capacity': max_capacity,
            'replacement_policy': replacement_policy
        }
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


def set_cache_properties(cache_properties):
    try:
        cnx = get_db()
        cursor = cnx.cursor(buffered = True)
        query_add = '''INSERT INTO cache_properties (max_capacity, replacement_policy) VALUES (%s,%s)'''
        cursor.execute(query_add,(cache_properties['max_capacity'], cache_properties['replacement_policy']))
        cnx.commit()
        return True
    except:
        return None


def total_active_node():
    global memcache_pool
    count=0
    active_list=[]
    for id, ip in memcache_pool.items():
        print("--------------------------------instance status: %s------------------------------" % ip)
        if not ip == None and not ip == 'Stopping' and not ip == "Starting":
            count+=1
            active_list.append((id,ip))
    return count, active_list


@webapp.route('/', methods=['GET', 'POST'])
def main():
    return get_response(True)


@webapp.route('/ready_request', methods=['GET', 'POST'])
def ready_request():
    global memcache_pool
    req_json = request.get_json(force=True)
    memcache_pool[req_json['instance_id']] = req_json['ip_address']
    print('New Memcache Host address:' + memcache_pool[req_json['instance_id']])
    notify = node_states()
    jsonReq={"message":notify}
    try:
        resp = requests.post("http://0.0.0.0:5000/show_notification", json=jsonReq)
    except:
        print("Frontend not started yet")
    return get_cache_response()


@webapp.route('/start_instance', methods=['GET', 'POST'])
def start_instance():
    instance_id = get_next_node()
    if not instance_id == None:
        print('Starting the instance ' + instance_id)
        memcache_pool[instance_id] = 'Starting'
        notify = node_states()
        jsonReq={"message":notify}
        try:
            resp = requests.post("http://0.0.0.0:5000/show_notification", json=jsonReq)
        except:
            print("Frontend not started yet")
        AWS_EC2_operator.start_instance(instance_id)

    return get_response(True)


@webapp.route('/stop_instance', methods=['GET', 'POST'])
def stop_instance():
    global memcache_pool
    instance_id = get_active_node()
    if not instance_id == None:
        print('Shutting down instance ' + instance_id)
        memcache_pool[instance_id] = 'Stopping'
        notify = node_states()
        jsonReq={"message":notify}
        try:
            resp = requests.post("http://0.0.0.0:5000/show_notification", json=jsonReq)
        except:
            print("Frontend not started yet")
        AWS_EC2_operator.shutdown_instance(instance_id)
    return get_response(True)


@webapp.route('/get_cache_info', methods = ['GET', 'POST'])
def get_cache_info():
    """
    Using the function to get all cache information including parameters and active instances to the frontend
    """
    global memcache_pool, pool_params
    cache_properties = get_memcache_properties()
    data = {
        'memcache_pool': memcache_pool,
        'cache_properties': cache_properties,
        'pool_params': pool_params 
    }

    return webapp.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )


@webapp.route('/refresh_configuration', methods = ['GET', 'POST'])
def refresh_configuration():
    global memcache_pool
    cache_properties = request.get_json(force=True)
    # Save to DB
    resp = set_cache_properties(cache_properties)
    if resp == True:
        for host in memcache_pool:
            ipv4 = memcache_pool[host]
            if not ipv4 == None and not ipv4 in stat: 
                # If an address is starting up, it will be set once it is ready
                address = 'http://' + str(ipv4) + ':5000/refresh_configuration'
                res = requests.post(address, json=cache_properties)

    return webapp.response_class(
            response = json.dumps("OK"),
            status=200,
            mimetype='application/json'
    )


@webapp.route('/set_memcache_pool_config', methods = ['GET', 'POST'])
def set_memcache_pool_config():
    global pool_params
    pool_params = request.get_json(force = True)
    return webapp.response_class(
            response = json.dumps("OK"),
            status=200,
            mimetype='application/json'
    )


@webapp.route('/get_memcache_pool_config', methods = ['GET', 'POST'])
def get_memcache_pool_config():
    global pool_params
    
    return webapp.response_class(
            response = json.dumps(pool_params),
            status=200,
            mimetype='application/json'
    )


@webapp.route('/clearMemcachePoolContent', methods = ['GET', 'POST'])
def clear_memcache_pool_content():
    for host in memcache_pool:
        ipv4 = memcache_pool[host]
        if not ipv4 == None and not ipv4 in stat:
            print('IP ' + ipv4)
            # Only need to clear active ports
            address = 'http://' + str(ipv4) + ':5000/clear_cache'
            res = requests.post(address)

    return webapp.response_class(
            response = json.dumps("OK"),
            status=200,
            mimetype='application/json'
    )


@webapp.route('/clear_data', methods = ['GET', 'POST'])
def clear_data():
    cnx = get_db()
    cursor = cnx.cursor(buffered = True)
    query_del = ''' DELETE * from images; '''
    cursor.execute(query_del)
    cnx.commit()

    clear_images()
    return webapp.response_class(
            response = json.dumps("OK"),
            status=200,
            mimetype='application/json'
    )


@webapp.route('/hash_key', methods = ['GET', 'POST'])
def hash_key():
    json_obj = request.get_json(force=True)
    key = json_obj['key']
    hash_val = hashlib.md5(key.encode()).hexdigest()
    hash_val = int(hash_val, base=16)
    index = (hash_val % 16)+1
    active_node,active_list = total_active_node()
    memcache_no = index % active_node
    return webapp.response_class(
            response = json.dumps(active_list[memcache_no]),
            status=200,
            mimetype='application/json'
    )


cache_properties = {
    'created_at': time.time(),
    'max_capacity': 10,
    'replacement_policy': 'Least Recently Used'
}


set_cache_properties(cache_properties)
startup_count = AWS_EC2_operator.update_memcachepool_status()
if startup_count == 0:
    start_instance()