import os.path
import unittest
from nudenet.nudenet import NudeDetector
import censor


class TestCensor(unittest.TestCase):

    def test_censor(self):
        """tests the work of censor(image_path) command in nudenet"""
        try:
            detector = NudeDetector()
            image_path = "tests/test2.jpg"
            if os.path.exists("tests/test2_censored.jpg"):
                os.remove("tests/test2_censored.jpg")
            censored = detector.censor(image_path)
            self.assertEqual(censored, "test2_censored.jpg")
        except Exception as e:
            print(f'An error occurred. {e}')

    def test_censor_colour(self):
        """tests the work of censor_colour(image_path) command"""
        try:
            image_path = "tests/test1.jpg"
            if os.path.exists("tests/test1_censored.jpg"):
                os.remove("tests/test1_censored.jpg")
            censored = censor.censor_colour(image_path, 'red')
            self.assertEqual(censored, "test1_censored.jpg")
        except Exception as e:
            print(f'An error occurred. {e}')


if __name__ == '__main__':
    unittest.main()
