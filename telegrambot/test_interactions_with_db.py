import unittest
from unittest.mock import patch, MagicMock
from trybot import handle_stats


@patch('trybot.telegrambot')
@patch('trybot.cursor')
class TestInteractionsWithDb(unittest.TestCase):
    def test_handle_stats(self, mock_cursor, mock_bot):
        test_cases = [
            {'count': 10,
             'chat_type': 'supergroup',
             'expected_message': "За следующее неприличное фото в чате пользователь Даня Викулов будет кикнут"},
            {'count': 1,
             'chat_type': 'supergroup',
             'expected_message': "Пользователь Лиза Петрова отправил 1 неприличных фото, "
                                 "за следующее - бан на 1 минуту"},
            {'count': 5,
             'chat_type': 'supergroup',
             'expected_message': "Пользователь Лиза Петрова отправил 5 неприличных фото, "
                                 "за следующее - бан на 5 минут"},
            {'count': 8,
             'chat_type': 'supergroup',
             'expected_message': "Пользователь Лиза Петрова отправил 8 неприличных фото, "
                                 "за следующее - бан на 60 минут"},

            {'count': 2,
             'chat_type': 'private',
             'expected_message': "невозможно узнать статистику"}
        ]
        try:
            for case in test_cases:
                mock_cursor.fetchone.return_value = (case['count'],)
                message = MagicMock()
                message.chat.type = case['chat_type']
                message.chat.id = 12345
                if case['count'] == 10:
                    message.from_user.first_name = 'Даня'
                    message.from_user.last_name = 'Викулов'
                else:
                    message.from_user.first_name = 'Лиза'
                    message.from_user.last_name = 'Петрова'

                handle_stats(message)

                mock_bot.send_message.assert_called_once_with(
                    12345,
                    case['expected_message']
                )
                mock_bot.send_message.reset_mock()
        except Exception as e:
            print(f'{e}')


if __name__ == '__main__':
    unittest.main()
