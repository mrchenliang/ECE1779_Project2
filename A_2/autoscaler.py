import  mysql.connector, requests, json, boto3, time
import pandas as pd
from botocore.exceptions import ClientError
from botocore.config import Config

memcache_node = ["i-0ca59c2326be01a9b","i-034ee52984dc9bd2e","i-0972b8c8d8d577ec0","i-07a760bbdad228a87","i-067ee0ffdf31ca474","i-033d4ce97a7e3f234","i-0a7a70f7ed4da4cbc","i-0f2bcbfa2224b03df"]

resp = requests.get("http://169.254.169.254/latest/user-data")
config = json.loads(resp.content.decode('utf-8'))

aws_config = {
  'aws_access_key_id': config['aws_access_key_id'],
  'awss_secret_access_key': config['aws_secret_access_key']
}

db_config = {'user': config["MySQL_user"],
             'password': config["MySQL_password"],
             'host': config["MySQL_host"],
             'port': '3306',
             'database': 'briandatabase'}

my_aws_config = Config(
    region_name = 'us-east-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

log_client = boto3.client('logs', region_name="us-east-1", aws_access_key_id=aws_config['aws_access_key_id'], aws_secret_access_key=aws_config['aws_secret_access_key'])
ec2_client = boto3.client('ec2', config=my_aws_config,aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])
backend = 'http://localhost:5002'


def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   port=db_config['port'],
                                   database=db_config['database']) 


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





