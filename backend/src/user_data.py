from flask_sqlalchemy import SQLAlchemy

data = SQLAlchemy()


class User(data.Model):
    id = data.Column(data.Integer, primary_key=True)
    username = data.Column(data.String(80), unique=True, nullable=False)
