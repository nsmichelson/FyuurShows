import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True


# DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/musicSiteApp'


# Connect to the database
#app = Flask('app.py')
app.config['SQLALCHEMY_DATABASE_URI']= SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
#app.config['ENV'] = 'development'
#app.config['DEBUG'] = True
