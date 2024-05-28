import logging

from flask import request, jsonify, Flask
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from data_create import db
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroupStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, nullable=False)
    count_test_messages_sent = db.Column(db.Integer, default=0, nullable=False)
    count_safe_photos_sent = db.Column(db.Integer, default=0, nullable=False)
    count_nsfw_photos_sent = db.Column(db.Integer, default=0, nullable=False)
    username = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref=db.backref('group_stats', lazy=True))


class MessageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text)
    is_text = db.Column(db.Boolean, default=False)
    is_nsfw = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref=db.backref('message_logs', lazy=True))


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


def get_stats(user_id, group_id):
    stats = GroupStats.query.filter_by(
        user_id=user_id,
        group_id=group_id
    ).first()

    if stats:
        user = User.query.get(user_id)
        return jsonify({
            'user_id': stats.user_id,
            'username': stats.username,
            'text_messages': stats.count_test_messages_sent,
            'safe_photos': stats.count_safe_photos_sent,
            'nsfw_photos': stats.count_nsfw_photos_sent,
            'graph_url': f'../backend/src/app/uploads/user_activity_{group_id}.png',
            'nsfw_url': f'../backend/src/app/uploads/nsfw_frequency_{user_id}.png',
            'top_users_url': f'../backend/src/app/uploads/top_users_{group_id}.png'
        }), 200


def draw_plot(group_id):
    messages = (MessageLog.query.filter_by(group_id=group_id)
                .order_by(MessageLog.timestamp.asc())
                .all())

    dates = [msg.timestamp.date() for msg in messages]
    counts = [dates.count(date) for date in dates]
    plt.figure(figsize=(10, 5))
    plt.bar(dates, counts)
    plt.xlabel('Дата')
    plt.ylabel('Количество сообщений')
    plt.title('Активность пользователей в группе')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'uploads/user_activity_{group_id}.png')
    plt.close()


def draw_user_stats(user_id, group_id):
    stats = GroupStats.query.filter_by(user_id=user_id, group_id=group_id).first()
    labels = ['Приличные фото', 'Неприличные фото']
    counts = [stats.count_safe_photos_sent, stats.count_nsfw_photos_sent]
    plt.figure(figsize=(10, 5))
    bars = plt.bar(labels, counts, color=['green', 'red'])
    plt.xlabel(f'Категории')
    plt.ylabel('Количество фото')
    plt.title(f'Пользователь {user_id}')
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height,
                 f'{height:.0f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(f'uploads/nsfw_frequency_{user_id}.png')
    plt.close()


def plot_top_users(group_id, top_n):
    top_users = (
        db.session.query(GroupStats.username, GroupStats.count_test_messages_sent)
        .filter_by(group_id=group_id)
        .order_by(GroupStats.count_test_messages_sent.desc())
        .limit(top_n)
        .all()
    )
    usernames = [user[0] for user in top_users]
    message_counts = [user[1] for user in top_users]
    plt.figure(figsize=(10, 5))
    plt.barh(usernames, message_counts)  # Горизонтальный bar chart
    plt.xlabel('Количество сообщений')
    plt.ylabel('Пользователи')
    plt.title(f'Топ-{top_n} самых активных пользователей')
    plt.tight_layout()
    plt.savefig(f'uploads/top_users_{group_id}.png')
    plt.close()
