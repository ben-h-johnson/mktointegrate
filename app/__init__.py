from flask import Flask
from flask_restful import Api
from flask.ext.sqlalchemy import SQLAlchemy
from app.mktorest import MarketoWrapper
#from flask.ext.login import LoginManager

app = Flask(__name__)
api = Api(app)
app.config.from_object('config')
db = SQLAlchemy(app)
#lm = LoginManager()
#lm.init_app(app)

mkto_client = mktorest.MarketoWrapper(os.environ['MKTO_MUNCHKIN'],
									 os.environ['MKTO_CLIENT_ID'],
									 os.environ['MKTO_CLIENT_SECRET'])

from app import views, models