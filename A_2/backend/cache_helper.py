from backend.database_helper import get_db

def get_cache():
    # get the cache properties from the database cache_properties
    try:
        cnx = get_db()
        cursor = cnx.cursor(buffered = True)
        query = '''SELECT * FROM cache_properties WHERE id = (SELECT MAX(id) FROM cache_properties LIMIT 1)'''
        cursor.execute(query)
        if(cursor._rowcount):
            cache=cursor.fetchone()
            return cache
        return None
    except:
        return None

def set_cache(max_capacity, replacement_policy):
    # put new cache properties into the database cache_properties
    try:
        cnx = get_db()
        cursor = cnx.cursor(buffered = True)
        query_add = ''' INSERT INTO cache_properties (max_capacity, replacement_policy) VALUES (%s,%s)'''
        cursor.execute(query_add,(max_capacity, replacement_policy))
        cnx.commit()
        return True
    except:
        return None