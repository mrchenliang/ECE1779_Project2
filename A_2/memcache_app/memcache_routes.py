from memcache_app import config, webapp, memcache, constants, startup
from flask import request
import json, datetime
global new_cache

@webapp.route('/put_into_memcache', methods = ['POST'])
def put_into_memcache():
    """ Put request to add key to memecache

        Parameters:
            request (Request): key and base64 image

        Return:
            response (JSON): "OK" or "ERROR"
    """
    req_json = request.get_json(force=True)
    key, value = list(req_json.items())[0]
    config.memcache_obj.pushitem(key, value)
    return get_response(True)

@webapp.route('/clear_cache', methods = ['GET', 'POST'])
def clear_cache():
    """ Clear cache values

        Return:
            response (JSON): "OK"
    """
    config.memcache_obj.clear_cache()
    return get_response(True)

@webapp.route('/get_from_memcache', methods = ['POST'])
def get_from_memcache():
    """ Get key from cache

        Parameters:
            request (Request): key

        Return:
            response: "OK" or "Key Not Found"
    """
    req_json = request.get_json(force=True)
    key = req_json["key"]
    response=config.memcache_obj.getitem(key)
    if response==None:
        return "Key Not Found"
        #check db and put into memcache
    else:
        return response

@webapp.route('/test/<key>/<value>')
def test(key,value):
    response=config.memcache_obj.pushitem(key,value)
    return get_response(response)

@webapp.route('/invalidate_specific_key', methods = ['POST'])
def invalidate_specific_key():
    """ Invalidate key in cache

        Parameters:
            request (Request): key

        Return:
            response (JSON): "OK"
    """
    req_json = request.get_json(force=True)
    config.memcache_obj.invalidate(req_json["key"])
    return get_response(True)

@webapp.route('/refresh_configuration', methods = ['POST'])
def refresh_configuration():
    """ Refresh configuration with new parameters
        Parameters:
            request (Request): Capacity and replacement policy
        Return:
            response (JSON): "OK"
    """
    print("In the Route")
    cache_properties = request.get_json(force=True)
    if not cache_properties == None:
        max_capacity = cache_properties['max_capacity']
        replacement_policy = cache_properties['replacement_policy']
        create_new_cache(replacement_policy, max_capacity)
        config.memcache_obj = new_cache
        return get_response(True)
    return None

@webapp.route('/get_statistics', methods = ['GET'])
def get_statistics():

    statistics = {
        'size_count': config.memcache_obj.current_size, 
        'request_count': config.memcache_obj.request_count,
        'miss_rate': config.memcache_obj.miss / config.memcache_obj.request_count,
        'key_count': config.memcache_obj.currsize,
        'hit_rate': config.memcache_obj.hit / config.memcache_obj.request_count
    }
    response = webapp.response_class(
            response=json.dumps(statistics),
            status=200,
            mimetype='application/json'
    )
    return response

def create_new_cache(replacement_policy, capacity):
    '''A new cache object is created and the previous cache
    values are added into it.
        Parameters:
            replacement_policy: string
            capacity: integer

        Return:
            True
    '''
    global new_cache
    print("capacity is:", capacity)
    if (replacement_policy == constants.LRU):
        new_cache = memcache.LRUMemCache(capacity)
    else:
        new_cache = memcache.RRMemCache(capacity)
    new_cache.maximum_size = capacity*pow(2,20)
    new_cache.replace_policy = replacement_policy
    data = config.memcache_obj._Cache__data
    for key,value in data.items():
        new_cache.pushitem(key, value)
    new_cache.request_count = config.memcache_obj.request_count
    new_cache.hit = config.memcache_obj.hit
    new_cache.miss = config.memcache_obj.miss
    return True

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

def get_response_no_key():
    response = webapp.response_class(
        response=json.dumps("Unknown key"),
        status=400,
        mimetype='application/json'
    )

    return response

def startup_app():
    print("Setting Params on start")
    cache_params = json.loads(startup.call_ready_request())
    capacity = cache_params['max_capacity']
    replacement_policy = cache_params['replacement_policy']
    create_new_cache(replacement_policy, capacity)
    config.memcache_obj = new_cache

startup_app()