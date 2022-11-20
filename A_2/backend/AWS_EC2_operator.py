import sys, boto3, threading, time
from botocore.exceptions import ClientError
from botocore.config import Config
from backend import memcache_pool
import os
# from frontend.constants import aws_config

my_aws_config = Config(
    region_name = 'us-east-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

ec2 = boto3.client('ec2',config=my_aws_config)


def instance_status_check(instance_id):
    """
    Using the function to check the status of a instance
    :param instance_id: Instance id
    :return: None
    """
    global memcache_pool
    # First using the Dry run to see whether we have the required permissions to get the status of the instance
    try:
        ec2.describe_instances(InstanceIds=[instance_id], DryRun=True)
        print('Instance Status')
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise
    # Dry run succeeded, run describe_instances without dryrun within the retry_times about 2 minutes
    retry_times = 0
    while(retry_times < 30):
        try:
            response = ec2.describe_instances(InstanceIds=[instance_id], DryRun=False)
            retry_times += 1
            resp_state = response['Reservations'][0]['Instances'][0]['State']['Name']
            print("Instance: " + instance_id + " state: " + resp_state)
            if resp_state == 'stopped':
                break
            time.sleep(4)
        except ClientError as e:
            print(e)
    # set the status of the instance in the memcache_pool to None        
    memcache_pool[instance_id] = None
    

def start_instance(instance_id):
    """
    Using the function to start an instance
    :param instance_id: Instance to start
    :return: None
    """
    print('Starting instance ' + instance_id)
    # First using the Dry run to see whether we have the required permissions to start the instance
    try:
        ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise
    # Dry run succeeded, run start_instances without dryrun
    try:
        response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
        print(response)
        print("Start instance %s successfully" % instance_id)
    except ClientError as e:
        print(e)


def shutdown_instance(instance_id):
    """
    Using the function to shut down an instance
    :param instance_id: Instance to shut down
    :return: None
    """
    print("Shutdown instance "+ instance_id)
    # First using the Dry run to see whether we have the required permissions to shutdown the instance
    try:
        ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise
    # Dry run succeeded, run stop_instances without dryrun
    try:
        response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
        th = threading.Thread(target=instance_status_check, args=(instance_id,))
        th.start()
        print(response)
        print("Stop instance %s successfully" % instance_id)
    except ClientError as e:
        print(e)


def update_memcache_pool_status():
    """
    Using the function to update the memcache instance node status in the memcache pool
    :param: None
    :return: Int
    """
    print("Checking the memcache pool status")
    instances = list(memcache_pool.keys())
    # First using the Dry run to see whether we have the required permissions to get the status of the instance
    try:
        ec2.describe_instances(InstanceIds=instances, DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise
    # Dry run succeeded, run describe_instances without dryrun
    running_node_count = 0
    try:
        for instance in instances:
            response = ec2.describe_instances(InstanceIds=[instance], DryRun=False)
            inst_name = response['Reservations'][0]['Instances'][0]['State']['Name']
            
            if (inst_name == 'running'):
                ip_address = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
                memcache_pool[instance] = ip_address
                running_node_count += 1
            elif inst_name == 'shutting-down' or inst_name == 'stopping':
                memcache_pool[instance] = 'Stopping'
            elif  inst_name == 'pending':
                memcache_pool[instance] = 'Starting'
            else:
                memcache_pool[instance] = None
        return running_node_count
    except ClientError as e:
        print(e)







