import requests, json, boto3, time
import pandas as pd
from botocore.exceptions import ClientError
from botocore.config import Config
from database_helper import *

memcache_node = ["i-0ca59c2326be01a9b","i-034ee52984dc9bd2e","i-0972b8c8d8d577ec0","i-07a760bbdad228a87","i-067ee0ffdf31ca474","i-033d4ce97a7e3f234","i-0a7a70f7ed4da4cbc","i-062be943d0df0ee8a"]

resp = requests.get("http://169.254.169.254/latest/user-data")
config = json.loads(resp.content.decode('utf-8'))

my_aws_config = Config(
    region_name = 'us-east-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

log_client = boto3.client('logs', region_name="us-east-1")
ec2_client = boto3.client('ec2', config=my_aws_config)
backend = 'http://0.0.0.0:5002'


def get_stats_logs():
    start_time = round((time.time() - 60) * 1000)
    current_time = round(time.time() * 1000)

    response = log_client.get_log_events(
        logGroupName='MetricLogs',
        logStreamName='ApplicationLogs',
        startTime=int(start_time),
        endTime=int(current_time),
        startFromHead=True
    )

    log_events = response['events']

    data = []
    for each_event in log_events:
        timestamp = each_event['timestamp']
        data_obj = json.loads(each_event['message'])
        data_obj['timestamp'] = timestamp * 1000000
        data.append(data_obj)

    data = pd.DataFrame(data)
    if not data.empty:
        data['timestamp']= pd.to_datetime(data['timestamp'])
        sample_data = data.resample('2Min', on='timestamp').mean()
        miss_rate = sample_data.iloc[-1]['miss_rate']
        
        return miss_rate
    return None


def get_pool_ready_count():
    global memcache_node

    active_count = 0
    unstable_count = 0
    try:
        ec2_client.describe_instances(InstanceIds=memcache_node, DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise
    try:
        for instance in memcache_node:
            response = ec2_client.describe_instances(InstanceIds=[instance], DryRun=False)
            inst_name = response['Reservations'][0]['Instances'][0]['State']['Name']
            if (inst_name == 'pending' or inst_name == 'shutting-down' or inst_name == 'stopping'):
                unstable_count += 1
            elif (inst_name == 'running'):
                active_count += 1
        return unstable_count, active_count
    except ClientError as e:
        print(e)


def get_memcache_policy():
    cnx = connect_to_database()
    cursor = cnx.cursor(buffered = True)
    query = '''SELECT * FROM cache_policies WHERE id = (SELECT MAX(id) FROM cache_policies LIMIT 1)'''
    cursor.execute(query)
    if(cursor._rowcount):# if key exists in db
        cache_policy=cursor.fetchone()
        cnx.close()
        return cache_policy
    cnx.close()
    return None


def auto_scaler():
    global backend

    print("----------------------------------------------------------------")
    print("Into the auto_scaler")
    print("----------------------------------------------------------------")
    while (True):
        print("----------------------------------------------------------------")
        print("Into the auto_scaler while loop")
        print("----------------------------------------------------------------")
        resp = requests.get(backend + "/get_memcache_pool_config")
        pool_params = json.loads(resp.content.decode('utf-8'))
        print(pool_params)
        if pool_params['mode'] == 'automatic':
            # runs every minute
            unstable_count, active_count = get_pool_ready_count()
            # Unstable implies instances are stil starting, stopping or pending
            print("Active Count " + str(active_count))
            print("Unstable Count " + str(unstable_count))

            if unstable_count == 0:
                miss_rate = get_stats_logs() * 100
                print("Current Miss Rate: " + str(miss_rate) + "%")
                # Miss rate is none, when no logs have been printed for this time period
                if not miss_rate == None:
                    cache_policy = get_memcache_policy()
                    print("--------------------------------")
                    print(cache_policy)
                    print("--------------------------------")
                    if not cache_policy == None:
                        if miss_rate > cache_policy[1]:
                            # Max Miss Rate, Scale up instances
                            print("Scale up")
                            expand_factor = cache_policy[3]
                            max_startup = round(expand_factor * active_count) - active_count
                            if max_startup + active_count > 8:
                                # Start a max of 8 nodes
                                max_startup = 8 - active_count
                            
                            for i in range(max_startup):
                                print("Call startup node")
                                requests.post(backend + '/start_instance')

                        # Get current memcache count, then scale up max 8
                        elif miss_rate < cache_policy[2]:
                            # Min Miss Rate, Scale up instances
                            print("Scale Down")
                            shrink_factor = cache_policy[4]
                            max_shutdown = active_count - round(shrink_factor * active_count)
                            if  active_count - max_shutdown < 1:
                                # Shutdown max of all but 1
                                max_shutdown = active_count - 1
                            
                            for i in range(max_shutdown):
                                print("Call shutdown node")
                                requests.post(backend + '/stop_instance')
        time.sleep(60)

auto_scaler()



