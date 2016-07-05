import os
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://localhost/intdemo')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True

SECRET_KEY = os.environ.get('FORM_KEY')
API_KEY = os.environ['API_KEY']