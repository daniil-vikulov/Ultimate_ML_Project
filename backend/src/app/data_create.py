import logging
import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_app(app):
    db.init_app(app)
    with app.app_context():
        check_and_create_db(app)


def check_and_create_db(app):
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if 'sqlite' in db_uri:
        db_path = db_uri.replace('sqlite:///', '')
        if not os.path.exists(db_path):
            db.create_all()
            print("Database is created")
        else:
            print("Database already exists")
    else:
        print("Using non-SQLite database. No need to check file existence.")
