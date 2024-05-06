from flask_sqlalchemy import SQLAlchemy

data = SQLAlchemy()


class User(data.Model):
    """
User model for the database.

Attributes:
id (int): Unique user ID, primary key.
username (str): A unique username, cannot be empty.

Example:
>>> user = User(username="example_user")
>>> user.id = None # ID will be assigned after adding the object to the database and committing it
    """
    id = data.Column(data.Integer, primary_key=True)
    username = data.Column(data.String(80), unique=True, nullable=False)
