from flask import Blueprint, render_template
import json
from managerapp.stat.stat_calculations import get_stat_logs

stat_routes = Blueprint("stat_routes", __name__)

@stat_routes.route('/memcache_stats')
def memcache_stats():
    stat_data = get_stat_logs()
    stat_data = json.dumps(stat_data)
    return render_template('stat.html', stat_data=stat_data)