#!/bin/sh
cd /home/ubuntu/ECE1779_Project2/A_2
pip install flask
pip install cachetools
pip install boto3
pip install botocore.exceptions
python3 run_memcache.py