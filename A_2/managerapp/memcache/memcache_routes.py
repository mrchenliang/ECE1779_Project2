
from flask import Blueprint
import requests, time
from flask import render_template, request, redirect
from managerapp.database_helper import get_db

memcache_routes = Blueprint("memcache_routes", __name__)

# Backend Host Port
backend_host = 'http://0.0.0.0:5002'

@memcache_routes.route('/memcache_manager', methods=['GET'])
def memcache_manager():
    max_capacity, replacement_policy, created_at, memcache_pool, node_data, pool_params, cache_policy = format_cache_settings()
    return render_template('manager.html',
        max_capacity=max_capacity,
        replacement_policy=replacement_policy,
        created_at=created_at,
        memcache_pool=memcache_pool,
        pool_params=pool_params,
        node_data=node_data,
        cache_policy=cache_policy)

@memcache_routes.route('/set_cache', methods = ['GET', 'POST'])
def memcache_properties():
    global backend_host
    if request.method == 'POST':
        new_capacity = request.form.get('max_capacity')
        if new_capacity.isdigit() and int(new_capacity) <= 2000:
            new_policy = request.form.get('replacement_policy')
            req = {
                'max_capacity': new_capacity, 
                'replacement_policy': new_policy, 
            }
            resp = requests.post(backend_host + '/refresh_configuration', json=req)
            max_capacity, replacement_policy, created_at, memcache_pool, node_data, pool_params, cache_policy = format_cache_settings()
            print(resp.json())
            if resp.json() == 'OK':
                return render_template('manager.html',
                max_capacity=max_capacity,
                replacement_policy=replacement_policy,
                created_at=created_at,
                memcache_pool=memcache_pool,
                pool_params=pool_params,
                node_data=node_data,
                cache_policy=cache_policy)
             
        # On error, reset to old params
        max_capacity, replacement_policy, created_at, memcache_pool, node_data, pool_params, cache_policy = format_cache_settings()
        return render_template('manager.html',
                max_capacity=max_capacity,
                replacement_policy=replacement_policy,
                created_at=created_at,
                memcache_pool=memcache_pool,
                pool_params=pool_params,
                node_data=node_data,
                status="TRUE",
                cache_policy=cache_policy)
        
    # On GET
    max_capacity, replacement_policy, created_at, memcache_pool, node_data, pool_params, cache_policy = format_cache_settings()
    return render_template('manager.html',
            max_capacity=max_capacity,
            replacement_policy=replacement_policy,
            created_at=created_at,
            memcache_pool=memcache_pool,
            pool_params=pool_params,
            node_data=node_data,
            cache_policy=cache_policy)

@memcache_routes.route('/clear_cache', methods=['GET', 'POST'])
def clear_cache():
    global backend_host
    if request.method == 'POST':
        res = requests.post(backend_host + '/clear_cache_pool')
    max_capacity, replacement_policy, created_at, memcache_pool, node_data, pool_params, cache_policy = format_cache_settings()
    return render_template('manager.html',
        max_capacity=max_capacity,
        replacement_policy=replacement_policy,
        created_at=created_at,
        memcache_pool=memcache_pool,
        pool_params=pool_params,
        node_data=node_data,
        cache_policy=cache_policy)

@memcache_routes.route('/clear_data', methods=['GET', 'POST'])
def clear_data():
    global backend_host
    if request.method == 'POST':
        res = requests.post(backend_host + '/clear_data')
    max_capacity, replacement_policy, created_at, memcache_pool, node_data, pool_params, cache_policy = format_cache_settings()
    return render_template('manager.html',
        max_capacity=max_capacity,
        replacement_policy=replacement_policy,
        created_at=created_at,
        memcache_pool=memcache_pool,
        pool_params=pool_params,
        node_data=node_data,
        cache_policy=cache_policy)


@memcache_routes.route('/set_pool_config', methods=['GET', 'POST'])
def set_pool_config():
    global backend_host
    if request.method == 'POST':
        if request.form.get("mode") == 'Manual Mode':
            
            if not request.form.get("pool-button") == None:
                manual_update_pool(request.form.get("pool-button"))
            pool_params = {
                'mode': 'manual',
            }
            requests.post(backend_host + "/set_memcache_pool_config", json=pool_params)
            max_capacity, replacement_policy, created_at, memcache_pool, node_data, pool_params, cache_policy = format_cache_settings()

            return render_template('manager.html',
                max_capacity=max_capacity,
                replacement_policy=replacement_policy,
                created_at=created_at,
                memcache_pool=memcache_pool,
                pool_params=pool_params,
                node_data=node_data,
                cache_policy=cache_policy,
                pool_status="TRUE")
        else:
            max_miss_rate = request.form.get("maxMiss")
            min_miss_rate = request.form.get("minMiss")
            expansion_ratio = request.form.get("expansionRatio")
            shrink_ratio = request.form.get("shrinkRatio") 
            if is_float(max_miss_rate) and is_float(min_miss_rate) and is_float(expansion_ratio) and is_float(shrink_ratio):
                max_miss_rate = float(max_miss_rate)
                min_miss_rate = float(min_miss_rate)
                expansion_ratio = float(expansion_ratio)
                shrink_ratio = float(shrink_ratio)
                if max_miss_rate > min_miss_rate and max_miss_rate >= 0 and min_miss_rate >= 0 and shrink_ratio >=0 and expansion_ratio >= 0:
                    cnx = get_db()
                    cursor = cnx.cursor(buffered=True)
                    query_add = ''' INSERT INTO cache_policies (max_miss_rate, min_miss_rate, expansion_ratio, shrink_ratio) VALUES (%s,%s,%s,%s)'''
                    cursor.execute(query_add,(max_miss_rate, min_miss_rate, expansion_ratio, shrink_ratio))
                    cnx.commit()
                    cnx.close()

                    pool_params = {
                        'mode': 'automatic',
                    }
                    requests.post(backend_host + "/set_memcache_pool_config", json=pool_params)
                
                    cache_policy = [0, max_miss_rate, min_miss_rate, expansion_ratio, shrink_ratio]
                    max_capacity, replacement_policy, created_at, memcache_pool, node_data, pool_params, cache_policy = format_cache_settings(cache_policy)
                    return render_template('manager.html',
                        max_capacity=max_capacity,
                        replacement_policy=replacement_policy,
                        created_at=created_at,
                        memcache_pool=memcache_pool,
                        pool_params=pool_params,
                        node_data=node_data,
                        cache_policy=cache_policy,
                        pool_status="TRUE")
        max_capacity, replacement_policy, created_at, memcache_pool, node_data, pool_params, cache_policy = format_cache_settings()
        return render_template('manager.html',
            max_capacity=max_capacity,
            replacement_policy=replacement_policy,
            created_at=created_at,
            memcache_pool=memcache_pool,
            pool_params=pool_params,
            node_data=node_data,
            cache_policy=cache_policy,
            pool_status="FALSE")        


    max_capacity, replacement_policy, created_at, memcache_pool, node_data, pool_params, cache_policy = format_cache_settings()
    return render_template('manager.html',
        max_capacity=max_capacity,
        replacement_policy=replacement_policy,
        created_at=created_at,
        memcache_pool=memcache_pool,
        pool_params=pool_params,
        node_data=node_data,
        cache_policy=cache_policy)


def format_cache_settings(cache_policy=None):
    global backend_host
    res = requests.get(backend_host + '/get_cache_info')
    print(res.json())
    memcache_pool = res.json()['memcache_pool']
    max_capacity = res.json()['cache_properties']['max_capacity'] 
    replacement_policy = res.json()['cache_properties']['replacement_policy'] 
    created_at = res.json()['cache_properties']['created_at']
    pool_params = res.json()['pool_params']

    i = 1
    stopping_nodes = 0
    starting_nodes = 0
    active_nodes = 0
    pool_data = []
    for id, ip_address in memcache_pool.items():
        if not ip_address == None:
            if ip_address == 'Starting' or ip_address == 'Stopping':
                pool_data.append(
                    { 'value': 1, 'name': 'Node ' + str(i) + ' ' + ip_address }
                )

            else:
                pool_data.append(
                    { 'value': 1, 'name': 'Node ' + str(i) }
                )
            i += 1
            
            if ip_address == 'Stopping':
                stopping_nodes += 1
            elif ip_address == 'Starting':
                starting_nodes += 1
            else:
                active_nodes += 1

    node_data = {
        'active': active_nodes,
        'stopping': stopping_nodes,
        'starting': starting_nodes
    }
    if cache_policy == None:
        cache_policy = [0, 0, 0, 0, 0]
        if pool_params['mode'] == 'automatic':
            cnx = get_db()
            cursor = cnx.cursor(buffered=True)
            query = '''SELECT * FROM cache_policies WHERE id = (SELECT MAX(id) FROM cache_policies LIMIT 1)'''
            cursor.execute(query)
            if(cursor._rowcount):# if key exists in db
                cache_policy=cursor.fetchone()
            cnx.commit()
            cnx.close()

    return max_capacity, replacement_policy, created_at, pool_data, node_data, pool_params, cache_policy

@memcache_routes.route('/navigate')
def navigate():
	hostname = request.headers.get('Host').split(':')[0]
	return redirect('http://'+hostname + ':5000')


def manual_update_pool(cmd):
    if cmd == 'increase':
        resp = requests.post(backend_host + '/start_instance')
    else:
        resp = requests.post(backend_host + '/stop_instance')

def is_float(value):
  try:
    float(value)
    return True
  except:
    return False

