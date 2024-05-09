import unittest
from unittest.mock import patch, MagicMock
from trybot import handle_photo, colour


@patch('trybot.bot')
@patch('trybot.censor_colour')
@patch('trybot.os')
class TestOs(unittest.TestCase):

    def test_colour(self, mock_os, mock_censor_colour, mock_bot):
        """tests the work of colour(call) function"""
        test_cases = [
            {'call_data': 'colour:black:test2.jpg',
             'expected_colour': 'black'},
            {'call_data': 'colour:white:test2.jpg',
             'expected_colour': 'white'},
            {'call_data': 'colour:blue:test2.jpg',
             'expected_colour': 'blue'},
            {'call_data': 'colour:green:test2.jpg',
             'expected_colour': 'green'},
            {'call_data': 'colour:orange:test2.jpg',
             'expected_colour': 'orange'},
            {'call_data': 'colour:violet:test2.jpg',
             'expected_colour': 'violet'}
        ]
        try:
            for case in test_cases:
                call = MagicMock()
                call.data = case['call_data']
                call.message = MagicMock()
                call.message.chat.id = 12345
                mock_censor_colour.return_value = f"test2_censored_{case['call_data'].split(':')[1]}.jpg"
                colour(call)
                mock_censor_colour.assert_called_once_with(case['call_data'].split(':')[2], case['expected_colour'])
                mock_bot.send_photo.assert_called_once_with(12345, any)
                mock_os.remove.assert_any_call(f"test2_censored_{case['call_data'].split(':')[1]}.jpg")
                mock_os.remove.assert_any_call('test2.jpg')
        except Exception as e:
            print(f'{e}')


if __name__ == '__main__':
    unittest.main()
