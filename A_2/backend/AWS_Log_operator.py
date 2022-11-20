import requests
import boto3, time, datetime, json
# from frontend.constants import aws_config
from backend import memcache_pool

# log_client = boto3.client('logs', region_name="us-east-1", aws_access_key_id=aws_config['aws_access_key_id'], aws_secret_access_key=aws_config['aws_secret_access_key'])
log_client = boto3.client('logs', region_name="us-east-1")

stat = ["Starting", "Stopping"]

pre_stats = {
    "miss_count": 0,
    "hit_count": 0,
}

def thread_stats():
    while True:
        statistics = get_aggregate_statistics()
        message = json.dumps(statistics)
        create_log(message)
        time.sleep(5)


def create_log(message):
    """
    Using the function to upload the log to the cloud watch logs
    :param message: The log message
    :return: None
    """
    uploadSequenceToken = None
    log_stream_resp = log_client.describe_log_streams(logGroupName="MetricLogs", logStreamNamePrefix="ApplicationLogs")
    if 'uploadSequenceToken' in log_stream_resp['logStreams'][0]:
        # Get previous Sequence Token if it exists
        uploadSequenceToken = log_stream_resp['logStreams'][0]['uploadSequenceToken']
    
    log_data = {
        "logGroupName": "MetricLogs",
        "logStreamName": "ApplicationLogs",
        "logEvents": [
            {
                "timestamp": int(round(time.time() * 1000)),
                "message": message
            }
        ]
    }

    if uploadSequenceToken:
        log_data['sequenceToken'] = uploadSequenceToken
    
    try:
        log_client.put_log_events(**log_data)
    except:
        print("upload logs error")


def get_aggregate_statistics():
    global memcache_pool, pre_stats
    statistics = {
        'key_count': 0,
        'size_count': 0,
        'request_count': 0,
        'miss_rate': 0,
        'hit_rate': 0,
        'active_count': 0
    }
    # Iterate the memcache in the pool to update the statistics
    for host in memcache_pool:
        ipv4 = memcache_pool[host]
        if not ipv4 == None and not ipv4 in stat:
            try:
                print("################################################################")
                print(ipv4)
                address = 'http://' + str(ipv4) + ':5000/get_statistics'
                response = requests.get(address)
                print(response.content.decode('utf-8'))
                response_dict = json.loads(response.content.decode('utf-8'))
                statistics['key_count'] += response_dict['key_count']
                statistics['size_count'] += response_dict['size_count']
                statistics['request_count'] += response_dict['request_count']
                statistics['hit_rate'] += response_dict['hit_rate']
                statistics['miss_rate'] += response_dict['miss_rate']
                statistics['active_count'] += 1
            except:
                print("Get statistics error")
    
    if statistics['active_count'] > 0:
        #rel_hit_rate, rel_miss_rate = update_rates(statistics['hit_rate'], statistics['miss_rate'])
        
        statistics_cur = {
            'key_count': statistics['key_count']/statistics['active_count'],
            'size_count': statistics['size_count']/statistics['active_count'],
            'request_count': statistics['request_count']/statistics['active_count'],
            'miss_rate': statistics['miss_rate']/statistics['active_count'],
            'hit_rate': statistics['hit_rate']/statistics['active_count'],
            'active_count': statistics['active_count']
        }

        pre_stats['miss_rate'] = statistics['miss_rate']
        pre_stats['hit_rate'] = statistics['hit_rate']

        return statistics_cur

    statistics = {
        'key_count': 0,
        'size_count': 0,
        'request_count': 0,
        'miss_rate': 0,
        'hit_rate': 0,
        'active_count': 0
    }
    return statistics


