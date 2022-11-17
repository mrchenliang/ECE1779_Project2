from flask import Blueprint, render_template
import json
from managerapp.stat.graph_helper import *
from managerapp.stat.stat_calculations import get_stats_logs

stat_routes = Blueprint("stat_routes", __name__)

@stat_routes.route('/cache_stats')
def new_stats():
    current_stats = get_stat_logs()
    current_stats = json.dumps(current_stats)
    return render_template('chart.html', stat_data=current_stats)