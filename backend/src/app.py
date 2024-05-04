from flask import Flask, request, jsonify
from nudenet import NudeClassifier
import os

from nudenet.nudenet import NudeDetector
from werkzeug.utils import secure_filename
from user_data import data, User
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
data.init_app(app)

classifier = NudeClassifier()
detector = NudeDetector()


@app.route('/<action>', methods=['POST'])
def upload_file(action):
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
    try:
        base_name, extension = os.path.splitext(os.path.basename(filepath))
        censored_filepath = os.path.join(app.config['UPLOAD_FOLDER'],  f"{base_name}_censored.jpg")
        detector.censor(filepath)
        return jsonify({'message': 'Image censored', 'censored_image_path': censored_filepath}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def classify_image(filepath):
    try:
        nudity_score = classifier.classify(filepath)
        return jsonify(nudity_score), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def detect_image(filepath):
    try:
        detected_parts = detector.detect(filepath)
        formatted_parts = [{'class': part['class'], 'score': part['score']} for part in detected_parts]
        return jsonify({'detected_parts': formatted_parts}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/register', methods=['POST'])
def register_user():
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
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'User not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
