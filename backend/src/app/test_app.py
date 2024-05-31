import unittest
from unittest.mock import patch, MagicMock
import os
from app import allowed_file, file_is_image, app, censor_image, classify_image, detect_image


class TestFileFunctions(unittest.TestCase):

    def test_allowed_file(self):
        self.assertTrue(allowed_file("test.jpg"))
        self.assertTrue(allowed_file("test.jpeg"))
        self.assertTrue(allowed_file("test.png"))
        self.assertFalse(allowed_file("test.txt"))
        self.assertFalse(allowed_file("test"))

    @patch("app.Image.open")
    def test_image_valid(self, mock_open):
        mock_open.return_value.verify = MagicMock()
        self.assertTrue(file_is_image("valid_image.jpg"))

    @patch("app.Image.open")
    def test_image_invalid(self, mock_open):
        mock_open.side_effect = IOError("Invalid image")
        self.assertFalse(file_is_image("invalid_image.jpg"))

    @patch("app.logger.error")
    @patch("app.Image.open")
    def test_file_is_image_logs_error(self, mock_open, mock_logger):
        mock_open.side_effect = IOError("Invalid image")
        file_is_image("invalid_image.jpg")
        mock_logger.assert_called_with("Invalid image file: Invalid image")


class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.test_image_path = 'test_image.jpg'
        with open(self.test_image_path, 'wb') as f:
            f.write(os.urandom(1024))

    def tearDown(self):
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)

    def test_no_file(self):
        response = self.app.post('/censor', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No file', response.data)

    def test_no_chosen_image(self):
        data = {'file': (self.test_image_path, '')}
        response = self.app.post('/censor', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No selected file', response.data)

    def test_invalid_type(self):
        data = {'file': (self.test_image_path, 'test.txt')}
        response = self.app.post('/censor', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'File type not allowed', response.data)

    @patch('app.allowed_file', return_value=True)
    @patch('app.file_is_image', return_value=False)
    def test_upload_file_invalid_image(self, mock_allowed_file, mock_file_is_image):
        data = {'file': (self.test_image_path, 'test.jpg')}
        response = self.app.post('/censor', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Uploaded file is not a valid image', response.data)

    @patch('app.allowed_file', return_value=True)
    @patch('app.file_is_image', return_value=True)
    @patch('app.process_image_file')
    def test_upload_file_process_image(self, mock_allowed_file, mock_file_is_image, mock_process_image_file):
        mock_process_image_file.return_value = ('{"result": "processed"}', 200)
        with open(self.test_image_path, 'rb') as img:
            data = {'file': (img, 'test.jpg')}
            response = self.app.post('/censor', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b'', response.data)

    @patch('app.allowed_file', return_value=True)
    @patch('app.file_is_image', return_value=True)
    @patch('app.process_image_file', side_effect=Exception('Ошибка при обработке изображения'))
    def test_upload_file_processing_error(self, mock_allowed_file, mock_file_is_image, mock_process_image_file):
        with open(self.test_image_path, 'rb') as img:
            data = {'file': (img, 'test.jpg')}
            response = self.app.post('/censor', data=data)
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'500 Internal Server Error', response.data)


class TestCensorImage(unittest.TestCase):
    @patch('app.detector.detect', return_value=[])
    @patch('app.jsonify', return_value=MagicMock())
    def test_censor_image_safe(self, mock_jsonify, mock_detect):
        filepath = 'uploads/test_image.jpg'
        response = censor_image(filepath)
        mock_detect.assert_called_once_with(filepath)
        mock_jsonify.assert_called_once_with({'message': 'Image safe', 'censored_image_path': filepath})
        self.assertEqual(response[1], 200)

    @patch('app.detector.detect', return_value=[{'class': 'NUDITY', 'score': 0.95}])
    @patch('app.detector.censor')
    @patch('app.jsonify', return_value=MagicMock())
    def test_censor_image_detected(self, mock_jsonify, mock_censor, mock_detect):
        filepath = 'uploads/test_image.jpg'
        response = censor_image(filepath)
        base_name, extension = os.path.splitext(os.path.basename(filepath))
        censored_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_censored{extension}")
        mock_detect.assert_called_once_with(filepath)
        mock_censor.assert_called_once_with(filepath)
        mock_jsonify.assert_called_once_with({'message': 'Image censored', 'censored_image_path': censored_filepath})
        self.assertEqual(response[1], 200)


class TestClassifyImage(unittest.TestCase):
    @patch('app.classifier.classify', return_value={'uploads/test_image.jpg': {'safe': 0, 'unsafe': 0}})
    @patch('app.jsonify', return_value=MagicMock())
    def test_classify_image_success(self, mock_jsonify, mock_classify):
        filepath = 'uploads/test_image.jpg'
        response = classify_image(filepath)
        mock_classify.assert_called_once_with(filepath)
        mock_jsonify.assert_called_once_with({'safe': 0, 'unsafe': 0})
        self.assertEqual(response[1], 200)

    @patch('app.classifier.classify', side_effect=Exception('Classification error'))
    @patch('app.jsonify', return_value=MagicMock())
    def test_classify_image_failure(self, mock_jsonify, mock_classify):
        filepath = 'uploads/test_image.jpg'
        response = classify_image(filepath)
        mock_classify.assert_called_once_with(filepath)
        mock_jsonify.assert_called_once_with({'error': 'Classification error'})
        self.assertEqual(response[1], 500)


class TestDetectImage(unittest.TestCase):
    @patch('app.detector.detect', return_value=[{'class': 'NUDITY', 'score': 0.95}])
    @patch('app.jsonify', return_value=MagicMock())
    def test_detect_image_success(self, mock_jsonify, mock_detect):
        filepath = 'uploads/test_image.jpg'
        response = detect_image(filepath)
        mock_detect.assert_called_once_with(filepath)
        mock_jsonify.assert_called_once_with({'detected_parts': [{'class': 'NUDITY', 'score': 0.95}]})
        self.assertEqual(response[1], 200)

    @patch('app.detector.detect', side_effect=Exception('Detection error'))
    @patch('app.jsonify', return_value=MagicMock())
    def test_detect_image_failure(self, mock_jsonify, mock_detect):
        filepath = 'uploads/test_image.jpg'
        response = detect_image(filepath)
        mock_detect.assert_called_once_with(filepath)
        mock_jsonify.assert_called_once_with({'error': 'Detection error'})
        self.assertEqual(response[1], 500)


if __name__ == '__main__':
    unittest.main()
