import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import logging
import os,base64
from frontend.constants import IMAGE_FOLDER

my_aws_config = Config(
    region_name = 'us-east-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

def clear_images():
    """
    Using this function to clear all images
    :return: bool
    """
    s3_clear = boto3.resource('s3',config=my_aws_config)
    bucket = s3_clear.Bucket('briansbucket')
    bucket.objects.all().delete()
    return True


def upload_file(file_name, bucket, s3=None, object_name=None):
    """
    Using this function to upload a file to an S3 bucket
    :param file_name: The uploading file
    :param bucket: The bucket to upload to
    :param s3: The AWS S3
    :param object_name: S3 object_name
    :return: bool
    """
    # Check if the object_name is given or not, if not, using the file_name as the object_name
    if object_name is None:
        object_name = os.path.basename(file_name)
        print("object created: %s" % object_name)

    # upload the file
    if s3 is None:
        s3 = boto3.client('s3',config=my_aws_config)
        print("s3 client created")
    try:
        response = s3.upload_file(Filename=file_name, Bucket=bucket, Key=object_name)
        print("Successfully uploaded file")
    except ClientError as e:
        logging.error(e)
        return False
    return True
    

def download_file(key,bucket='briansbucket',s3=None):
    """
    Using this function to download a file from an S3 bucket
    :param key: The downloading file
    :param bucket: The bucket to download from
    :param s3: The AWS S3
    :return: bool or base64 encoded image
    """
    if s3 is None:
        s3 = boto3.client('s3',config=my_aws_config)
        print("s3 client created")
    try:
        with open('Temp.txt', 'r+b') as file:
            s3.download_fileobj(bucket, key, file)
            base64_image = file.read().decode('utf-8')
        print("downloaded")
        return base64_image
    except ClientError as e:
        logging.error(e)
        return False