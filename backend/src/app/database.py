import logging

from flask import request, jsonify, Flask

from data_create import db
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def create_group_id_tables(group_id):
#     # Table for photos sent with timestamp to know when a photo is sent
#     photo_table_name = f'group_{group_id}_photos_sent'
#     if not db.engine.has_table(photo_table_name):
#         class Photo(db.Model):
#             __tablename__ = photo_table_name
#             id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#             user_id = db.Column(db.Integer, nullable=False)
#             username = db.Column(db.String(80), nullable=False)
#             group_id = db.Column(db.Integer, nullable=False)
#             nsfw_photo = db.Column(db.Integer, nullable=False, default=0)  # 0 safe, 1 not safe
#             timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#
#         db.create_all()
#
#     # Table for user statistics
#     stats_table_name = f'group_{group_id}_user_stats'
#     if not db.engine.has_table(stats_table_name):
#         class UserStats(db.Model):
#             __tablename__ = stats_table_name
#             id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#             user_id = db.Column(db.Integer, nullable=False)
#             group_id = db.Column(db.Integer, nullable=False)
#             count_safe_photos_sent = db.Column(db.Integer, nullable=False, default=0)
#             count_nsfw_photos_sent = db.Column(db.Integer, nullable=False, default=0)
#             count_messages_sent = db.Column(db.Integer, nullable=False, default=0)
#
#         db.create_all()

class GroupStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, nullable=False)
    count_test_messages_sent = db.Column(db.Integer, default=0)
    count_safe_photos_sent = db.Column(db.Integer, default=0)
    count_nsfw_photos_sent = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref=db.backref('group_stats', lazy=True))

    # def __repr__(self):
    #     return f'<GroupStats {self.user_id} in group {self.group_id}>'


# db.create_all()


class MessageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text)
    is_text = db.Column(db.Boolean, default=False)
    is_nsfw = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('message_logs', lazy=True))

    # def __repr__(self):
    #     return f'<MessageLog {self.id}>'


# db.create_all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False)
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
    if 'user_id' not in request_data:
        return jsonify({'error': 'User ID is required'}), 400
    if 'username' not in request_data:
        return jsonify({'error': 'Username is required'}), 400
    if 'group_id' not in request_data:
        return jsonify({'error': 'Group ID is required'}), 400
    if not validate_user_id(request_data['user_id']):
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
    user_id = int(request_data['user_id'])
    username = request_data['username'].strip()
    group_id = int(request_data['group_id'])

    # existing_user = User.query.filter_by(id=id_writing).first()
    # existing_username = User.query.filter_by(username=username).first()

    # Проверка на наличие пользователя с таким же ID или именем пользователя в базе данных
    # if existing_user:
    #     logger.error(f"ID {id_writing} already exists.")
    #     return jsonify({'error': 'ID already exists'}), 409

    # if existing_username:
    #     logger.error(f"Username {username} already exists.")
    #     return jsonify({'error': 'Username already exists'}), 409

    # Если нет пользователя с таким же ID или именем пользователя, добавляем его в базу данных
    try:
        new_user = User(user_id=user_id, username=username, group_id=group_id)
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
    stats = [{'id': user.id, 'user_id': user.user_id, 'username': user.username, 'group_id': user.group_id} for user in users]
    return jsonify(stats), 200


