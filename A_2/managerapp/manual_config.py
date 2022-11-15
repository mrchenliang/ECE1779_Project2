import boto3
import time
from managerapp import webapp, current_pool_size, instance_pool
from managerapp import config

ec2 = boto3.resource('ec2')
EC2 = boto3.client('ec2')
CLOUDWATCH = boto3.client('cloudwatch')

'''
Function to expand the pool
'''


@webapp.route('/add_node', methods=['POST'])
def add_node():
    if current_pool_size[0] >= 8:
        error_msg = 'Reach max pool size. Cannot expand more.'
        response = webapp.response_class(
            response=error_msg,
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        # Create a new instance
        current_pool_size[0] += 1
        new_instance = ec2_create()
        new_instance_id = new_instance['Instances'][0]['InstanceId']
        # Loop until the status of the new instance is running in order to register to elb.
        status = EC2.describe_instance_status(InstanceIds=[new_instance_id])
        # At beginning, the status['InstanceStatuses'] is empty, it needs time to generate info
        while len(status['InstanceStatuses']) < 1:
            time.sleep(1)
            status = EC2.describe_instance_status(InstanceIds=[new_instance_id])
        # It needs time to transfer the state from 'pending' to 'running'
        while status['InstanceStatuses'][0]['InstanceState']['Name'] != 'running':
            time.sleep(1)
            status = EC2.describe_instance_status(InstanceIds=[new_instance_id])
        instance_pool.append(new_instance)
        error_msg = 'Expanding the pool by one node.'
        response = webapp.response_class(
            response=error_msg,
            status=200,
            mimetype='application/json'
        )
        return response



def ec2_create():
    # Create a new ec2 instance
    new_instance = EC2.run_instances(ImageId=config.image_id,
                                     KeyName=config.key_name,
                                     MinCount=1,
                                     MaxCount=1,
                                     UserData=config.user_data,
                                     InstanceType='t2.micro',
                                     Monitoring={'Enabled': True},
                                     SecurityGroupIds=config.SecurityGroup_id,  # copy security group
                                     IamInstanceProfile=config.Iam_profile  # copy IAM role
                                     )
    # Get the new instance id
    return new_instance


'''
Function to shrink the pool
'''


@webapp.route('/shrink_node', methods=['POST'])
# Terminate a EC2 instance
def shrink_node():
    if current_pool_size[0] == 1:
        error_msg = 'Reach min pool size. Cannot shrink more.'
        response = webapp.response_class(
            response=error_msg,
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        current_pool_size[0] -= 1
        terminate_id = instance_pool[-1]['InstanceId']
        ec2.instances.filter(InstanceIds=[terminate_id]).terminate()
        instance_pool.pop()
        error_msg = 'Shrinking the pool by one node.'
        response = webapp.response_class(
            response=error_msg,
            status=200,
            mimetype='application/json'
        )
        return response

