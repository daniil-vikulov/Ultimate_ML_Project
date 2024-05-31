import logging
import os

import cv2
from PIL import Image
from flask import Flask, request, jsonify
from nudenet.classifier import Classifier as NudeClassifier
from nudenet.nudenet import NudeDetector
from werkzeug.utils import secure_filename

import data_create
from colours import colours
from data_create import db
from database import User, GroupStats, MessageLog, get_stats, draw_plot, draw_user_stats, plot_top_users, draw_nsfw_plot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
data_create.init_app(app)

classifier = NudeClassifier()
detector = NudeDetector()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def file_is_image(filepath):
    try:
        with Image.open(filepath) as img:
            img.verify()
        return True
    except (IOError, SyntaxError) as e:
        logger.error(f"Invalid image file: {e}")
        return False


@app.route('/<action>', methods=['POST'])
def upload_file(action):
    """
    Handles file upload to the server for a specified action.
    :param: action (str): The action to be performed with the uploaded file.
    Must be one of the allowed actions specified in ALLOWED_ACTIONS.

    :return: Flask Response: Returns a JSON response with the processing result or an error.

    :errors: 400: Returned if the specified action is not supported, no file is provided, a file with no name is selected,
     the file type is not allowed, or the uploaded file is not a valid image.
    """
    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        logger.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        logger.error("File type is not allowed")
        return jsonify({'error': 'File type not allowed'}), 400

    # Secure the filename and save the file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Validate if the uploaded file is a valid image
    if not file_is_image(filepath):
        os.remove(filepath)
        logger.error("Uploaded file is not a valid image")
        return jsonify({'error': 'Uploaded file is not a valid image'}), 400

    return process_image_file(filepath, action)


def process_image_file(filepath, action):
    """
    Processes an image file based on the specified action.
    :param: filepath (str): The path to the image file that needs to be processed.
        action (str): The type of processing to be performed on the image. Supported actions include 'censor',
         'classify', and 'detect'.

    :return: Depending on the action:
        - For 'censor': Returns the result of censoring sensitive content in the image.
        - For 'classify': Returns the classification results of the image.
        - For 'detect': Returns the detection results from the image.

        If an exception occurs during processing, it returns a JSON response with an error message
        and a status code of 500.
    """
    try:
        if action == 'censor':
            return censor_image(filepath)
        elif action == 'classify':
            return classify_image(filepath)
        elif action == 'detect':
            return detect_image(filepath)
        elif action == 'censor_colour':
            colour = request.form.get('colour')
            if not colour:
                return jsonify({'error': 'Colour is required for censor_colour action'}), 400
            return censor_image_with_colour(filepath, colour)
    except Exception as e:
        logger.exception("Error processing image")
        return jsonify({'error': str(e)}), 500


def censor_image(filepath):
    """
    Censors nudity in an image and saves the censored image.
    :param filepath: Path to the image to be censored.
    :return: JSON response with a message, path to the censored image, save censored image named
    '{base_name}_censored.jpg' into folder /backend/src/uploads
    """
    logger.info(f"Censoring image at {filepath}")
    try:
        base_name, extension = os.path.splitext(os.path.basename(filepath))
        censored_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_censored{extension}")
        detections = detector.detect(filepath)
        face_classes = ['FACE_FEMALE', 'FACE_MALE']
        only_face_classes = all(detection["class"] in face_classes for detection in detections)
        if not detections or only_face_classes:
            logger.info(f"Image safe")
            return jsonify({'message': 'Image safe', 'censored_image_path': filepath}), 200
        detector.censor(filepath)
        logger.info(f"Image censored successfully. Saved to {censored_filepath}")
        return jsonify({'message': 'Image censored', 'censored_image_path': censored_filepath}), 200
    except Exception as e:
        logger.exception("Failed to censor image")
        return jsonify({'error': str(e)}), 500


def censor_colour(image_path, colour, classes=None, output_path=None):
    """
    Censors specific areas of an image based on detected classes by filling them with a specified colour.
    :param:
        image_path (str): Path to the input image.
        colour (str): Name of the colour to use for censoring.
        classes (list, optional): A list of class names to censor. If none, all detected classes are censored, defaults to None.
        output_path (str, optional): The path to save the censored image.
    :return: None
    """
    if classes is None:
        classes = []
    detections = detector.detect(image_path)
    face_classes = ['FACE_FEMALE', 'FACE_MALE']
    only_face_classes = all(detection["class"] in face_classes for detection in detections)
    if classes:
        detections = [detection for detection in detections if detection["class"] in classes]
    img = cv2.imread(image_path)

    # Apply censoring to the detected areas
    for detection in detections:
        c = detection["class"]
        box = detection["box"]
        x, y, w, h = box[0], box[1], box[2], box[3]
        if not only_face_classes or c not in face_classes:
            img[y: y + h, x: x + w] = colours[colour]

    if output_path:
        cv2.imwrite(output_path, img)
        logging.info(f"Censored image saved to '{output_path}'")


def censor_image_with_colour(filepath, colour):
    """
    Censors an image by filling detected objects with a specified colour and saves the result.
    :param:
        filepath (str): The path to the input image.
        colour (str): The name of the colour to use for censoring.
    :return: tuple: A Flask JSON response with a message and the path to the censored image, and an HTTP status code.
    """
    logger.info(f"Censoring image at {filepath} with colour {colour}")
    try:
        base_name, extension = os.path.splitext(os.path.basename(filepath))
        censored_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_censored{extension}")
        censor_colour(filepath, colour, output_path=censored_filepath)
        logger.info(f"Image censored successfully. Saved to {censored_filepath}")
        return jsonify({'message': 'Image censored with colour', 'censored_image_path': censored_filepath}), 200
    except Exception as e:
        logger.exception("Failed to censor image with colour")
        return jsonify({'error': str(e)}), 500


def classify_image(filepath):
    """
    Classifies an image for nudity content.
    :param filepath: Path to the image to be classified.
    :return: JSON response with classification scores for 'safe' and 'unsafe'.
    """
    logger.info(f"Classifying image at {filepath}")
    try:
        nudity_score = classifier.classify(filepath)
        results = nudity_score.get(filepath, {})
        safe_score = round(results.get('safe', 0), 3)
        unsafe_score = round(results.get('unsafe', 0), 3)
        rounded_scores = {'safe': safe_score, 'unsafe': unsafe_score}
        logger.info("Image classified successfully")
        return jsonify(rounded_scores), 200
    except Exception as e:
        logger.exception("Failed to classify image")
        return jsonify({'error': str(e)}), 500


def detect_image(filepath):
    """
    Detects nudity in an image and returns parts detected.
    :param filepath: Path to the image where detection is performed.
    :return: JSON response with detected parts and their scores.
    """
    logger.info(f"Detecting nudity in image at {filepath}")
    try:
        detected_parts = detector.detect(filepath)
        formatted_parts = [{'class': part['class'], 'score': round(part['score'], 3)} for part in
                           detected_parts]
        logger.info("Nudity detected successfully")
        return jsonify({'detected_parts': formatted_parts}), 200
    except Exception as e:
        logger.exception("Failed to detect nudity in image")
        return jsonify({'error': str(e)}), 500


@app.route('/message', methods=['POST'])
def log_message():
    """
    Logs a message and updates user and group statistics.
    :param
    - username: The username of the sender
    - user_id: The ID of the user
    - group_id: The ID of the group
    - message: The content of the message
    - is_text: Boolean indicating if the message is text
    - is_nsfw: Boolean indicating if the message is NSFW
    :return: JSON response indicating success or failure.
    """
    data = request.get_json()
    username = data.get('username')
    user_id = data.get('user_id')
    group_id = data.get('group_id')
    message = data.get('message')
    is_text = data.get('is_text')
    is_nsfw = data.get('is_nsfw')

    logger.info(f"Received message from user_id={user_id}, group_id={group_id}")
    try:
        user = User.query.get(user_id)
        if not user:
            logger.info(f"Creating new user with user_id={user_id}")
            user = User(user_id=user_id, group_id=group_id, username=username)
            db.session.add(user)
        group_stats = GroupStats.query.filter_by(
            user_id=user_id,
            group_id=group_id,
            username=username
        ).first()
        if not group_stats:
            logger.info(f"Creating new group stats for user_id={user_id} and group_id={group_id}")
            group_stats = GroupStats(user_id=user_id, group_id=group_id, username=username)
            db.session.add(group_stats)
            db.session.commit()
        if is_text:
            group_stats.count_test_messages_sent += 1
        elif is_nsfw:
            group_stats.count_nsfw_photos_sent += 1
        else:
            group_stats.count_safe_photos_sent += 1

        db.session.commit()
        message_log = MessageLog(
            user_id=user_id,
            group_id=group_id,
            username=username,
            message=message,
            is_text=is_text,
            is_nsfw=is_nsfw
        )
        db.session.add(message_log)
        db.session.commit()

        logger.info(f"Message logged for user_id={user_id}, group_id={group_id}")
        return jsonify({'message': 'Data is saved'}), 201

    except Exception as e:
        logger.exception("Error saving data")
        return jsonify({'error': 'Server error'}), 500


@app.route('/stats/<group_id>/<user_id>')
def get_user_stats(group_id, user_id):
    """
    Endpoint to retrieve and visualize user statistics in a group.
    :param group_id: ID of the group
        user_id: ID of the user
    :return: JSON response with user statistics or an error message if stats are not found or server error occurs.
    """
    logger.info(f"Fetching stats for user_id={user_id} in group_id={group_id}")
    try:
        draw_plot(group_id)
        draw_nsfw_plot(group_id)
        draw_user_stats(group_id)
        plot_top_users(group_id)
        stats = GroupStats.query.filter_by(user_id=user_id, group_id=group_id).first()

        if stats:
            logger.info(f"Stats found for user_id={user_id} in group_id={group_id}")
            return get_stats(user_id, group_id)
        else:
            logger.warning(f"No stats found for user_id={user_id} in group_id={group_id}")
            return jsonify({'message': 'No stats found'}), 404

    except Exception as e:
        logger.exception("Error fetching statistics")
        return jsonify({'error': 'Server error'}), 500


@app.route('/group_stats/<group_id>')
def get_group_stats(group_id):
    """
    Endpoint to retrieve and visualize group statistics.
    :param group_id: ID of the group.
    :return:JSON response with group statistics or an error message if stats are not found or server error occurs.
    """
    logger.info(f"Fetching group stats for group_id={group_id}")

    try:
        top_nsfw_users = (db.session.query(GroupStats)
                          .filter(GroupStats.group_id == group_id)
                          .order_by(GroupStats.count_nsfw_photos_sent.desc())
                          .all())

        top_active_users = (db.session.query(GroupStats)
                            .filter(GroupStats.group_id == group_id)
                            .order_by((GroupStats.count_test_messages_sent +
                                       GroupStats.count_safe_photos_sent +
                                       GroupStats.count_nsfw_photos_sent).desc())
                            .all())

        response_data = {
            'top_nsfw_users': [
                {'user_id': stats.user_id, 'username': stats.username, 'nsfw_count': stats.count_nsfw_photos_sent}
                for stats in top_nsfw_users
            ],
            'top_active_users': [
                {'user_id': stats.user_id, 'username': stats.username,
                 'total_messages': (stats.count_test_messages_sent +
                                    stats.count_safe_photos_sent +
                                    stats.count_nsfw_photos_sent)}
                for stats in top_active_users
            ]
        }
        logger.info(f"Successfully fetched group stats for group_id={group_id}")
        return jsonify(response_data), 200

    except Exception as e:
        logger.exception(f"Error fetching group stats for group_id={group_id}")
        return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    app.run(debug=True)
