from flask import Flask, render_template, url_for, request, send_file, json, jsonify, g
from memcache import webapp
from memcache.response_helper import response_builder
from memcache.memcache_operator import *


@webapp.route('/put_into_memcache', methods=['GET', 'POST'])
def put_memcache():
    request_json = request.get_json(force=True)
    key, file = list(request_json.items())[0]
    flag = put_into_memcache(key, file)
    return response_builder(flag)


@webapp.route('/get_from_memcache', methods=['GET', 'POST'])
def get_memcache():
    request_json = request.get_json(force=True)
    key = request_json['key']
    file = get_from_memcache(key)
    if file == None:
        return 'Key Not Found'
    else:
        return file


@webapp.route('/clear_cache', methods=['GET', 'POST'])
# clears the memcache object
def clear_cache():
    flag = clear_all_from_memcache()
    return response_builder(flag)


@webapp.route('/refresh_configuration', methods=['GET', 'POST'])
# refresh the memcache configuration
def refresh_configuration():
    flag = refresh_config_of_memcache()
    return response_builder(flag)


@webapp.route('/invalidate_specific_key', methods=['GET', 'POST'])
def invalidate_key():
    request_json = request.get_json(force=True)
    key = request_json['key']
    flag = invalidate_specific_key(key)
    return response_builder(flag)
