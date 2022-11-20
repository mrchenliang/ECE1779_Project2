import boto3, time, json, pandas as pd
from datetime import datetime
from numpy import NaN
# from frontend.constants import aws_config

client = boto3.client('logs', region_name="us-east-1")

def get_stat_logs():
    HALF_HOUR = 30*60
    start_time = round((time.time() - HALF_HOUR) * 1000)
    current_time = round(time.time() * 1000)

    response = client.get_log_events(
        logGroupName = 'MetricLogs',
        logStreamName = 'ApplicationLogs',
        startTime = int(start_time),
        endTime = int(current_time),
        startFromHead = True
    )

    log_events = response['events']

    data = []

    for event in log_events:
        timestamp = event['timestamp']
        data_object = json.loads(event['message'])
        data_object['timestamp'] = timestamp * 1000000
        data.append(data_object)

    data = pd.DataFrame(data) 

    if not data.empty:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        sample_data = data.resample('1Min', on='timestamp').mean()
        
        data_array = [
            list(sample_data.index.values.astype(datetime)),
            list(sample_data['size_count'].values),
            list(sample_data['miss_rate'].values),
            list(sample_data['hit_rate'].values),
            list(sample_data['key_count'].values),
            list(sample_data['request_count'].values),
            list(sample_data['active_count'].values)
        ]

        return data_array
    
    data_array = [[], [], [], [], [], [], []]
    return data_array