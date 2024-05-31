import logging
from datetime import timedelta

import matplotlib.dates as mdates
from flask import request, jsonify
from matplotlib import pyplot as plt

from backend.src.app.data_create import db

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
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
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
        return {
            'user_id': stats.user_id,
            'username': stats.username,
            'text_messages': stats.count_test_messages_sent,
            'safe_photos': stats.count_safe_photos_sent,
            'nsfw_photos': stats.count_nsfw_photos_sent,
            'graph_url': f'uploads/user_activity_{group_id}.png',
            'nsfw_url': f'uploads/nsfw_frequency_{group_id}.png',
            'top_users_url': f'uploads/top_users_{group_id}.png',
            'nsfw_stats_graph': f'uploads/nsfw_activity_{group_id}.png'
        }, 200


def draw_plot(group_id):
    messages = (MessageLog.query.filter_by(group_id=group_id)
                .order_by(MessageLog.timestamp.asc())
                .all())

    if not messages:
        print(f"No messages found for group {group_id}")
        return
    timestamps = {}
    start_time = messages[0].timestamp.replace(minute=0, second=0, microsecond=0)
    end_time = messages[-1].timestamp.replace(minute=0, second=0, microsecond=0) + timedelta(hours=3)
    current_time = start_time

    while current_time <= end_time:
        timestamps[current_time] = 0
        current_time += timedelta(hours=3)
    for msg in messages:
        msg_time = msg.timestamp.replace(minute=0, second=0, microsecond=0)
        for time in timestamps:
            if msg_time <= time:
                timestamps[time] += 1
    dates = list(timestamps.keys())
    counts = list(timestamps.values())
    plt.figure(figsize=(12, 6))
    plt.plot(dates, counts, marker='o', linestyle='-', color='#1f77b4', linewidth=2, markersize=6)

    for i, (date, count) in enumerate(zip(dates, counts)):
        if i == 0 or counts[i] != counts[i - 1]:
            plt.text(date, count, str(count), fontsize=10, ha='right', va='bottom', color='#1f77b4', fontweight='bold')

    plt.xlabel('Дата', fontweight='bold', fontsize=12)
    plt.ylabel('Количество сообщений', fontweight='bold', fontsize=12)
    plt.title('Активность пользователей в группе', fontsize=14, fontweight='bold')
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=3))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))
    plt.gcf().autofmt_xdate()
    plt.style.use('ggplot')
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.grid(True, which='major', linestyle='--', alpha=0.7)
    ax.xaxis.grid(True, which='minor', linestyle=':', alpha=0.4)
    ax.set_facecolor('#f9f9f9')
    plt.tight_layout()
    plt.savefig(f'uploads/user_activity_{group_id}.png')
    plt.close()


def draw_nsfw_plot(group_id):
    messages = (MessageLog.query.filter_by(group_id=group_id, is_nsfw=True)
                .order_by(MessageLog.timestamp.asc())
                .all())

    timestamps = {}
    start_time = messages[0].timestamp.replace(minute=0, second=0, microsecond=0)
    end_time = messages[-1].timestamp.replace(minute=0, second=0, microsecond=0) + timedelta(hours=3)
    current_time = start_time

    while current_time <= end_time:
        timestamps[current_time] = 0
        current_time += timedelta(hours=3)

    for msg in messages:
        msg_time = msg.timestamp.replace(minute=0, second=0, microsecond=0)
        for time in timestamps:
            if msg_time <= time:
                timestamps[time] += 1
    dates = list(timestamps.keys())
    counts = list(timestamps.values())
    plt.figure(figsize=(12, 6))
    plt.plot(dates, counts, marker='o', linestyle='-', color='#ff6347', linewidth=2, markersize=6)
    for i, (date, count) in enumerate(zip(dates, counts)):
        if i == 0 or counts[i] != counts[i - 1]:
            plt.text(date, count, str(count), fontsize=10, ha='right', va='bottom', color='#ff6347', fontweight='bold')
    plt.xlabel('Дата', fontweight='bold', fontsize=12)
    plt.ylabel('Количество NSFW фото', fontweight='bold', fontsize=12)
    plt.title('Активность пользователей в группе (NSFW фото)', fontsize=14, fontweight='bold')

    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=3))
    plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))
    plt.gcf().autofmt_xdate()
    plt.style.use('ggplot')
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.grid(True, which='major', linestyle='--', alpha=0.7)
    ax.xaxis.grid(True, which='minor', linestyle=':', alpha=0.4)
    ax.set_facecolor('#f9f9f9')
    plt.tight_layout()
    plt.savefig(f'uploads/nsfw_activity_{group_id}.png')
    plt.close()


def draw_user_stats(group_id):
    stats = GroupStats.query.filter_by(group_id=group_id).all()

    usernames = [stat.username for stat in stats]
    safe_counts = [stat.count_safe_photos_sent for stat in stats]
    nsfw_counts = [stat.count_nsfw_photos_sent for stat in stats]

    x = range(len(usernames))
    width = 0.4

    plt.figure(figsize=(12, 6))

    bars_safe = plt.bar(x, safe_counts, width=width, color='green', align='center', label='Приличные фото')
    bars_nsfw = plt.bar([i + width for i in x], nsfw_counts, width=width, color='red', align='center',
                        label='Неприличные фото')

    plt.xlabel('Пользователи', fontweight='bold', fontsize=12)
    plt.ylabel('Количество фото', fontweight='bold', fontsize=12)
    plt.title('Количество приличных и неприличных фото по пользователям', fontsize=14, fontweight='bold')

    plt.xticks([i + width / 2 for i in x], usernames, rotation=45, ha='right')

    for bar in bars_safe:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}', ha='center', va='bottom', color='green',
                 fontweight='bold')

    for bar in bars_nsfw:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}', ha='center', va='bottom', color='red',
                 fontweight='bold')

    plt.legend()
    ax = plt.gca()
    ax.set_facecolor('#f9f9f9')
    plt.tight_layout()
    plt.savefig(f'uploads/nsfw_frequency_{group_id}.png')
    plt.close()


def plot_top_users(group_id):
    top_users = (
        db.session.query(GroupStats.username, GroupStats.count_test_messages_sent)
        .filter_by(group_id=group_id)
        .order_by(GroupStats.count_test_messages_sent.desc())
        .all()
    )

    usernames = [user[0] for user in top_users]
    message_counts = [user[1] for user in top_users]

    plt.figure(figsize=(12, 8))
    bars = plt.barh(usernames, message_counts, color='#1f77b4')

    plt.xlabel('Количество сообщений', fontweight='bold', fontsize=12)
    plt.ylabel('Пользователи', fontweight='bold', fontsize=12)
    plt.title('Топ самых активных пользователей', fontsize=14, fontweight='bold')

    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height() / 2, f'{width:.0f}',
                 ha='left', va='center', color='black', fontweight='bold')

    plt.style.use('ggplot')

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.yaxis.grid(False)
    ax.set_facecolor('#f9f9f9')

    plt.tight_layout()
    plt.savefig(f'uploads/top_users_{group_id}.png')
    plt.close()
