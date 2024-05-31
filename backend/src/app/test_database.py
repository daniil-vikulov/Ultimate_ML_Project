import unittest
from unittest.mock import patch, MagicMock

from flask import Flask

from database import register_user, login_user, validate_request


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('database.User')
    @patch('database.db')
    def test_register_user(self, mock_db, mock_user):
        mock_request_data = {
            'user_id': '1',
            'username': 'test_user',
            'group_id': '1'
        }
        mock_user_ = MagicMock()
        mock_user.return_value = mock_user_

        with self.app.test_request_context(json=mock_request_data):
            response = register_user()

        self.assertEqual(response[1], 201)
        self.assertEqual(response[0].json, {'message': 'User registered successfully'})
        mock_db.session.add.assert_called_once_with(mock_user_)
        mock_db.session.commit.assert_called_once()

    @patch('database.User')
    @patch('database.db')
    def test_register_user_error(self, mock_db, mock_user):
        mock_request_data = {
            'username': 'test_user',
            'group_id': '1'
        }

        with self.app.test_request_context(json=mock_request_data):
            response = register_user()

        self.assertEqual(response[1], 400)
        self.assertIn('error', response[0].json)

    @patch('database.User')
    @patch('database.db')
    def test_register_user_exception(self, mock_db, mock_user):
        mock_request_data = {
            'user_id': '1',
            'username': 'test_user',
            'group_id': '1'
        }
        mock_db.session.commit.side_effect = Exception('DB Error')

        with self.app.test_request_context(json=mock_request_data):
            response = register_user()

        self.assertEqual(response[1], 500)
        self.assertIn('error', response[0].json)
        mock_db.session.rollback.assert_called_once()

    @patch('database.User')
    def test_login_user(self, mock_user):
        mock_request_data = {
            'user_id': '1',
            'username': 'test_user',
            'group_id': '1'
        }
        mock_user.query.filter_by.return_value.first.return_value = MagicMock(username='test_user')

        with self.app.test_request_context(json=mock_request_data):
            response = login_user()

        self.assertEqual(response[1], 200)
        self.assertEqual(response[0].json, {'message': 'Login successful'})

    @patch('database.User')
    def test_login_user_404(self, mock_user):
        mock_request_data = {
            'user_id': '1',
            'username': 'test_user',
            'group_id': '1'
        }
        mock_user.query.filter_by.return_value.first.return_value = None

        with self.app.test_request_context(json=mock_request_data):
            response = login_user()

        self.assertEqual(response[1], 404)
        self.assertEqual(response[0].json, {'error': 'User not found'})

    def test_validate_request(self):
        mock_request_data = {
            'user_id': '1',
            'username': 'test_user',
            'group_id': '1'
        }
        with self.app.test_request_context(json=mock_request_data):
            response = validate_request(mock_request_data)
        self.assertIsNone(response)

    def test_validate_request_no_user_id(self):
        mock_request_data = {
            'username': 'test_user',
            'group_id': '-123'
        }
        with self.app.test_request_context(json=mock_request_data):
            response = validate_request(mock_request_data)
        self.assertEqual(response[1], 400)
        self.assertEqual(response[0].json, {'error': 'User ID is required'})

    def test_validate_request_invalid_user_id(self):
        mock_request_data = {
            'user_id': 'abc',
            'username': 'test_user',
            'group_id': '-123'
        }
        with self.app.test_request_context(json=mock_request_data):
            response = validate_request(mock_request_data)
        self.assertEqual(response[1], 400)
        self.assertEqual(response[0].json, {'error': 'User ID must be a number'})

    def test_validate_request_no_username(self):
        mock_request_data = {
            'user_id': '123',
            'group_id': '-123'
        }
        with self.app.test_request_context(json=mock_request_data):
            response = validate_request(mock_request_data)
        self.assertEqual(response[1], 400)
        self.assertEqual(response[0].json, {'error': 'Username is required'})

    def test_validate_request_invalid_username(self):
        mock_request_data = {
            'user_id': '123',
            'username': '',
            'group_id': '-123'
        }
        with self.app.test_request_context(json=mock_request_data):
            response = validate_request(mock_request_data)
        self.assertEqual(response[1], 400)
        self.assertEqual(response[0].json, {'error': 'Username cannot be empty'})

    def test_validate_request_no_group_id(self):
        mock_request_data = {
            'user_id': '123',
            'username': 'test_user'
        }
        with self.app.test_request_context(json=mock_request_data):
            response = validate_request(mock_request_data)
        self.assertEqual(response[1], 400)
        self.assertEqual(response[0].json, {'error': 'Group ID is required'})

    def test_validate_request_invalid_group_id(self):
        mock_request_data = {
            'user_id': '123',
            'username': 'test_user',
            'group_id': 'abc'
        }
        with self.app.test_request_context(json=mock_request_data):
            response = validate_request(mock_request_data)
        self.assertEqual(response[1], 400)
        self.assertEqual(response[0].json, {'error': 'Group ID must be a number'})


if __name__ == '__main__':
    unittest.main()
