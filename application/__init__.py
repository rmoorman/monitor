from flask import Flask
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app, '/api')
db = SQLAlchemy(app)
