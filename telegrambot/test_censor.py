import os.path
import unittest
from nudenet.nudenet import NudeDetector
import censor


class TestCensor(unittest.TestCase):

    def test_censor(self):
        try:
            detector = NudeDetector()
            image_path = "test2.jpg"
            if os.path.exists("test2_censored.jpg"):
                os.remove("test2_censored.jpg")
            censored = detector.censor(image_path)
            self.assertEqual(censored, "test6_censored.jpg")
        except Exception as e:
            print(f'An error occurred. {e}')

    def test_censor_colour(self):
        try:
            image_path = "test1.jpg"
            if os.path.exists("test1_censored.jpg"):
                os.remove("test1_censored.jpg")
            censored = censor.censor_colour(image_path, 'red')
            self.assertEqual(censored, "test1_censored.jpg")
        except Exception as e:
            print(f'An error occurred. {e}')


if __name__ == '__main__':
    unittest.main()
