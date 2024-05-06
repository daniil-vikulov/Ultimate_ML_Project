import os
import tempfile
import pytest
import random
import string

from app import app, data


@pytest.fixture
def test_client():
    data_fd, data_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{data_path}'
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            data.create_all()
        yield client

    os.close(data_fd)
    os.remove(data_path)


def create_random_username(prefix="user", size=6):
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))
    return f"{prefix}{suffix}"


test_username = create_random_username()


def test_user_registration(test_client):
    resp = test_client.post('/register', json={'username': test_username})
    assert resp.status_code == 201
    assert b'User registered successfully' in resp.data


def test_user_login(test_client):
    test_client.post('/register', json={'username': test_username})
    resp = test_client.post('/login', json={'username': test_username})
    assert resp.status_code == 200
    assert b'Login successful' in resp.data


def test_login_with_unregistered_user(test_client):
    resp = test_client.post('/login', json={'username': 'unknown_user'})
    assert resp.status_code == 404
    assert b'User not found' in resp.data


def test_file_upload(test_client):
    with open('uploads/test_image.jpg', 'rb') as img:
        file_data = {'file': (img, 'test_image.jpg')}
        resp = test_client.post('/classify', content_type='multipart/form-data', data=file_data)
        assert resp.status_code == 200


def test_image_classification(test_client):
    with open('uploads/test_image.jpg', 'rb') as img:
        file_data = {'file': (img, 'test_image.jpg')}
        resp = test_client.post('/classify', content_type='multipart/form-data', data=file_data)
        assert resp.status_code == 200


if __name__ == '__main__':
    pytest.main()
