from managerapp import webapp, pool_size, instance_pool, frontend_info, config_mode, pool_stats
import requests
from flask import render_template, url_for, request
from flask import json
import os
import re
import boto3


@webapp.route('/manual_config', methods=['GET', 'POST'])
def manual_config():
    # switch to manual mode
    config_mode['mode'] = 'Manual'
