import logging
import os

from PIL import Image
from flask import Flask, request, jsonify
from nudenet.classifier import Classifier as NudeClassifier
from nudenet.nudenet import NudeDetector
from werkzeug.utils import secure_filename

import data_create
import database
from censor import censor_colour

# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.join(current_dir, '../../../')
#
# # Добавление корневой директории в sys.path
# sys.path.append(project_root)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_ACTIONS = {'censor', 'classify', 'detect', 'register', 'login', 'stats'}

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
    if action not in ALLOWED_ACTIONS:
        logger.error("Invalid action")
        return jsonify({'error': 'Invalid action'}), 400

    if action == 'register':
        return database.register_user()

    if action == 'stats':
        return database.get_stats()

    if action == 'login':
        return database.login_user()

        # Check if there's a file part in the request
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
            colour = request.args.get('colour')
            if not colour:
                return jsonify({'error': 'Missing colour parameter'}), 400
            return censor_colour_image(filepath, colour=colour)
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
        censored_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_censored.jpg")
        detector.censor(filepath)
        logger.info(f"Image censored successfully. Saved to {censored_filepath}")
        return jsonify({'message': 'Image censored', 'censored_image_path': censored_filepath}), 200
    except Exception as e:
        logger.exception("Failed to censor image")
        return jsonify({'error': str(e)}), 500


def censor_colour_image(filepath, colour):
    try:
        base_name, extension = os.path.splitext(os.path.basename(filepath))
        censored_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_censored.jpg")
        censor_colour(filepath, colour)
        if os.path.exists(censored_filepath):
            return jsonify({'message': 'Image censored', 'censored_image_path': censored_filepath}), 200
        else:
            return jsonify({'error': 'Image censoring failed'}), 500
    except Exception as e:
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
        formatted_parts = [{'class': part['class'].lower(), 'score': round(part['score'], 3)} for part in
                           detected_parts]
        logger.info("Nudity detected successfully")
        return jsonify({'detected_parts': formatted_parts}), 200
    except Exception as e:
        logger.exception("Failed to detect nudity in image")
        return jsonify({'error': str(e)}), 500


# def validate_username(username):
#     if not username or not username.strip():
#         logger.error("Username is required and cannot be empty.")
#         return False
#     return True
#
#
# def validate_request(request_data):
#     if 'username' not in request_data:
#         return jsonify({'error': 'Username is required'}), 400
#     if not validate_username(request_data['username']):
#         return jsonify({'error': 'Username cannot be empty'}), 400
#     return None
#
#
# @app.route('/register', methods=['POST'])
# def register_user():
#     """
#     Registers a new user with a unique username.
#     :return: JSON response indicating success or failure of user registration.
#     """
#     request_data = request.get_json()
#     validation_error = validate_request(request_data)
#     if validation_error:
#         return validation_error
#
#     username = request_data['username'].strip()
#     existing_user = User.query.filter_by(username=username).first()
#
#     # Checking the presence of a user in the database
#     if existing_user:
#         logger.error(f"Username {username} already exists.")
#         return jsonify({'error': 'Username already exists'}), 409
#
#     # If there is no username, add it to the database
#     try:
#         new_user = User(username=username)
#         data.session.add(new_user)
#         data.session.commit()
#         logger.info(f"User {username} registered successfully.")
#         return jsonify({'message': 'User registered successfully'}), 201
#     except Exception as e:
#         data.session.rollback()
#         logger.exception("Failed to register user due to unexpected error")
#         return jsonify({'error': str(e)}), 500
#
#
# @app.route('/login', methods=['POST'])
# def login_user():
#     """
#     Logs in a user by username.
#     :return: JSON response indicating whether the login was successful or not.
#     """
#     request_data = request.get_json()
#     validation_error = validate_request(request_data)
#     if validation_error:
#         return validation_error
#
#     username = request_data['username'].strip()
#     user = User.query.filter_by(username=username).first()
#     if user:
#         logger.info(f"Login successful for {username}")
#         return jsonify({'message': 'Login successful'}), 200
#
#     logger.error(f"User {username} not found")
#     return jsonify({'error': 'User not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
