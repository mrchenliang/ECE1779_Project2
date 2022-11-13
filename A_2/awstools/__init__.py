from flask import Flask
import datetime

webapp = Flask(__name__)

try:
    from awstools import awsEC2

except Exception as e:
    print("No AWS Tools")
    print("Error: ", e)
