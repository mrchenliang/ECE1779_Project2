from flask import Blueprint, render_template
import json
from managerapp.stat.stat_calculations import get_stat_logs

stat_routes = Blueprint("stat_routes", __name__)

@stat_routes.route('/memcache_stats')
def memcache_stats():
    current_stats = get_stat_logs()
    current_stats = json.dumps(current_stats)
    return render_template('stat.html', stat_data=current_stats)