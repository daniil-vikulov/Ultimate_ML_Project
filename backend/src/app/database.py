import logging

from flask import request, jsonify

from data_create import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    group_id = db.Column(db.Integer, nullable=False)


def validate_username(username):
    if not username or not username.strip():
        logger.error("Username is required and cannot be empty.")
        return False
    return True


def validate_group_id(group_id):
    if not group_id or not str(group_id).isdigit():
        logger.error("Group ID must be a number.")
        return False
    return True


def validate_user_id(user_id):
    if not user_id or not str(user_id).isdigit():
        logger.error("User ID must be a number.")
        return False
    return True


def validate_request(request_data):
    if 'id' not in request_data:
        return jsonify({'error': 'User ID is required'}), 400
    if 'username' not in request_data:
        return jsonify({'error': 'Username is required'}), 400
    if 'group_id' not in request_data:
        return jsonify({'error': 'Group ID is required'}), 400
    if not validate_user_id(request_data['id']):
        return jsonify({'error': 'User ID must be a number'}), 400
    if not validate_username(request_data['username']):
        return jsonify({'error': 'Username cannot be empty'}), 400
    if not validate_group_id(request_data['group_id']):
        return jsonify({'error': 'Group ID must be a number'}), 400
    return None


def register_user():
    request_data = request.get_json()
    validation_error = validate_request(request_data)
    if validation_error:
        return validation_error

    user_id = int(request_data['id'])
    username = request_data['username'].strip()
    group_id = int(request_data['group_id'])

    existing_user = User.query.filter_by(id=user_id).first()
    existing_username = User.query.filter_by(username=username).first()

    # Проверка на наличие пользователя с таким же ID или именем пользователя в базе данных
    if existing_user:
        logger.error(f"User ID {user_id} already exists.")
        return jsonify({'error': 'User ID already exists'}), 409

    if existing_username:
        logger.error(f"Username {username} already exists.")
        return jsonify({'error': 'Username already exists'}), 409

    # Если нет пользователя с таким же ID или именем пользователя, добавляем его в базу данных
    try:
        new_user = User(id=user_id, username=username, group_id=group_id)
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User {username} registered successfully.")
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        logger.exception("Failed to register user due to unexpected error")
        return jsonify({'error': str(e)}), 500


def login_user():
    request_data = request.get_json()
    validation_error = validate_request(request_data)
    if validation_error:
        return validation_error

    username = request_data['username'].strip()
    user = User.query.filter_by(username=username).first()
    if user:
        logger.info(f"Login successful for {username}")
        return jsonify({'message': 'Login successful'}), 200

    logger.error(f"User {username} not found")
    return jsonify({'error': 'User not found'}), 404


def get_stats():
    users = User.query.all()
    stats = [{'id': user.id, 'username': user.username, 'group_id': user.group_id} for user in users]
    return jsonify(stats), 200
