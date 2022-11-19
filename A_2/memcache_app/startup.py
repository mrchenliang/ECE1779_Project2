import requests, os
import boto3
from botocore.exceptions import ClientError

instance_id_main = "i-0d6cb94ff6e44bdfc" # Main host

ec2 = boto3.client('ec2', region_name='us-east-1')

def call_ready_request():
    try:
        ec2.describe_instances(InstanceIds=[instance_id_main], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    try:
        print("################################################################")
        response = ec2.describe_instances(InstanceIds=[instance_id_main], DryRun=False)

        resp = requests.get("http://169.254.169.254/latest/meta-data/public-ipv4")
        instance_ip_address = resp.content.decode("utf-8")

        resp = requests.get("http://169.254.169.254/latest/meta-data/instance-id")
        instance_id = resp.content.decode("utf-8")

        print(instance_ip_address)
        print(instance_id)

        host_ip_address = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        address = 'http://' + str(host_ip_address) + ':5002/ready_request'
        req_json = {
            "ip_address": instance_ip_address,
            "instance_id": instance_id
        }
        res = requests.post(address, json=req_json)
        print("Cache Parameter Response")
        print(res.content.decode("utf-8"))
        return res.content.decode("utf-8")
    except ClientError as e:
        print(e)
