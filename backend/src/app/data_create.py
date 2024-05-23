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
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        db.create_all()
        logger.info("Database created")
    else:
        logger.info("Database already exists")
