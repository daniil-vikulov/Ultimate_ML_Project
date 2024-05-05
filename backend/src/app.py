from flask import Flask, request, jsonify
from nudenet import NudeClassifier
import os

from nudenet.nudenet import NudeDetector
from werkzeug.utils import secure_filename
from user_data import data, User
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
"""
Upload the image to the folder "/uploads" (it will be created automatically when the server starts) 
The censored images will appear there too
"""
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
data.init_app(app)

classifier = NudeClassifier()
detector = NudeDetector()


@app.route('/<action>', methods=['POST'])
def upload_file(action):
    """
    Process an uploaded file based on the action provided in the URL.
    :param action: Specifies the action to be performed on the uploaded image.
                   Options are 'censor', 'classify', and 'detect'.
                   !The file must be passed as part of the request with the "file" label.
    :return: JSON response with the result of the specified action or an error message.

    Answers:
    - "200 OK": Successful file processing. Returns results depending on the action.
    - "201 Created": Successful creation of a new user account
    - "400 Bad Request": File upload error (e.g. file not found or not selected).
    - "404 Not Found": Server cannot find what was requested: the user is trying to log in with a username that
        does not exist in the database
    - "409 Conflict": Server is trying to register a new user with a username that is already occupied
    - "500 Internal Server Error": Fatal server error when processing a file.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        if action == 'censor':
            return censor_image(filepath)
        elif action == 'classify':
            return classify_image(filepath)
        elif action == 'detect':
            return detect_image(filepath)
    return jsonify({'error': 'File upload failed'}), 500


def censor_image(filepath):
    """
    Censors nudity in an image and saves the censored image.
    :param filepath: Path to the image to be censored.
    :return: JSON response with a message, path to the censored image, save censored image named
    '{base_name}_censored.jpg' into folder /backend/src/uploads
    """
    try:
        base_name, extension = os.path.splitext(os.path.basename(filepath))
        censored_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_censored.jpg")
        detector.censor(filepath)
        return jsonify({'message': 'Image censored', 'censored_image_path': censored_filepath}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def classify_image(filepath):
    """
    Classifies an image for nudity content.
    :param filepath: Path to the image to be classified.
    :return: JSON response with classification scores for 'safe' and 'unsafe'.
    """
    try:
        nudity_score = classifier.classify(filepath)
        results = nudity_score.get(filepath, {})
        safe_score = round(results.get('safe', 0), 3)
        unsafe_score = round(results.get('unsafe', 0), 3)
        rounded_scores = {'safe': safe_score, 'unsafe': unsafe_score}
        return jsonify(rounded_scores), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def detect_image(filepath):
    """
    Detects nudity in an image and returns parts detected.
    :param filepath: Path to the image where detection is performed.
    :return: JSON response with detected parts and their scores.
    """
    try:
        detected_parts = detector.detect(filepath)
        formatted_parts = [{'class': part['class'].lower(), 'score': round(part['score'], 3)} for part in
                           detected_parts]
        return jsonify({'detected_parts': formatted_parts}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/register', methods=['POST'])
def register_user():
    """
    Registers a new user with a unique username.
    :return: JSON response indicating success or failure of user registration.
    """
    username = request.json.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    new_user = User(username=username)
    data.session.add(new_user)
    try:
        data.session.commit()
    except IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login_user():
    """
    Logs in a user by username.
    :return: JSON response indicating whether the login was successful or not.
    """
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'User not found'}), 404


"""
Usage examples (enter commands in terminal):
    - Image censor request:
curl -X POST -F "file=@path_to_image.jpg" http://localhost:5000/censor

    - Request for image classification:
curl -X POST -F "file=@path_to_image.jpg" http://localhost:5000/classify

    - Request to detect objects in the image:
curl -X POST -F "file=@path_to_image.jpg" http://localhost:5000/detect

If you are in the folder "/uploads" , then just write the name of the uploaded file instead of "path_to_image"
"""

if __name__ == '__main__':
    app.run(debug=True)
