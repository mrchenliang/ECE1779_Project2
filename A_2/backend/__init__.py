from flask import Flask
import os

global IMAGE_FOLDER

webapp = Flask(__name__)

IMAGE_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/static/images'

from backend import main