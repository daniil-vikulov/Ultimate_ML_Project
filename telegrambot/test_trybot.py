import unittest
from unittest.mock import patch, MagicMock

from trybot import handle_start, handle_help, handle_mute, handle_kick, handle_test, write_ans, next_img


@patch('trybot.bot')
class TestTrybot(unittest.TestCase):

    def test_handle_start(self, mock_bot):
        """tests the work of /start command"""
        message = MagicMock()
        if message.chat.type == 'supergroup':
            try:
                message.chat.id = 12345
                handle_start(message)
                mock_bot.send_message.assert_called_once_with(12345,
                                                              f'Привет всем! Этот бот будет следить за порядком в чате\n'
                                                              f'Нельзя слать неприличные фото, '
                                                              f'за это бан')
            except Exception as e:
                print(f'{e}')
        else:
            message.chat.id = 12345
            message.from_user.first_name = 'Лиза'
            handle_start(message)
            mock_bot.send_message.assert_called_once_with(12345,
                                                          f'Привет, Лиза! '
                                                          f'Проверь свое фото на наличие неприличного контента')

    def test_handle_help(self, mock_bot):
        """tests the work of /help command"""
        message = MagicMock()
        if message.chat.type == 'supergroup':
            try:
                message.chat.id = 12345
                handle_help(message)
                mock_bot.send_message.assert_called_once_with(12345,
                                                              f'Если надоел какой-то пользователь, то можно замутить его командой /mute\n'
                                                              f'Также можно кикнуть /kick '
                                                              f'(просто ответьте на сообщение пользователя, который надоел)\n'
                                                              f'Если вы админ и хотите получить статистику нарушителей чата, '
                                                              f'используйте /stats\n'
                                                              f'Если вы участник чата, то по команде /stats можно узнать свою статистику\n'
                                                              f'Если вы хотите посмотреть на визуализацию статистики в чате, используйте /plots')
            except Exception as e:
                print(f'{e}')
        else:
            try:
                message.chat.id = 12345
                message.from_user.first_name = 'Лиза'
                handle_help(message)
                mock_bot.send_message.assert_called_once_with(12345,
                                                              f'Лиза!\n'
                                                              f'Для того, чтобы протестировать работу сервиса, '
                                                              f'воспользуйтесь командой /test'
                                                              f' или просто отправьте фото\n')
            except Exception as e:
                print(f'{e}')

    def test_handle_test(self, mock_bot):
        """tests the work of /test command"""
        message = MagicMock()
        if message.chat.type == 'supergroup':
            return
        else:
            try:
                message.chat.id = 12345
                message.from_user.first_name = 'Лиза'
                handle_test(message)
                mock_bot.send_message.assert_called_once_with(12345,
                                                              'хотите проверить фото на наличие '
                                                              'непристойного контента?', reply_markup=any)
                keyboard = mock_bot.send_message.call_args[1]['reply_markup']
                self.assertEqual(len(keyboard.keyboard), 2)
                self.assertEqual(keyboard.keyboard[0][0].text, "да")
                self.assertEqual(keyboard.keyboard[0][0].callback_data, "test.yes")
                self.assertEqual(keyboard.keyboard[1][1].text, "нет")
                self.assertEqual(keyboard.keyboard[1][1].callback_data, "test.no")
            except Exception as e:
                print(f'{e}')

    def test_write_ans(self, mock_bot):
        """tests the work of write_ans function"""
        call = MagicMock()
        if call.chat.type == 'supergroup':
            return
        else:
            if call.data == "test.yes":
                try:
                    call.message.chat.id = 12345
                    write_ans(call)
                    mock_bot.send_message.assert_called_once_with(12345,
                                                                  "отправьте фото на проверку:)))))))")
                except Exception as e:
                    print(f'{e}')
            elif call.data == "test.no":
                try:
                    call.message.chat.id = 12345
                    write_ans(call)
                    mock_bot.send_message.assert_called_once_with(12345,
                                                                  "квак плак, не больно то надо")
                except Exception as e:
                    print(f'{e}')

    def test_handle_mute(self, mock_bot):
        """tests the work of /mute command"""
        message = MagicMock()
        if message.chat.type == 'supergroup':
            try:
                if message.reply_to_message:
                    message.chat.id = 12345
                    message.reply_to_message = MagicMock()
                    message.reply_to_message.from_user.id = 67890
                    message.reply_to_message.from_user.username = 'hihihi'
                    handle_mute(message)
                    mock_bot.restrict_chat_member.assert_called_once()
                    call_args = mock_bot.restrict_chat_member.call_args[1]
                    self.assertEqual(call_args['chat_id'], 12345)
                    self.assertEqual(call_args['user_id'], 67890)
                    self.assertIsInstance(call_args['until_date'], int)
                    mock_bot.send_message.assert_called_once_with(12345,
                                                                  f"Пользователь @{message.reply_to_message.from_user.username}"
                                                                  f" замучен на 60 секунд.")
                else:
                    message.chat.id = 12345
                    handle_mute(message)
                    mock_bot.send_message.assert_called_once_with(12345,
                                                                  "Пожалуйста, ответьте на сообщение пользователя, "
                                                                  "которого надо замутить")
            except Exception as e:
                print(f'{e}')
        else:
            try:
                message.chat.id = 12345
                handle_mute(message)
                mock_bot.send_message.assert_called_once_with(12345,
                                                              'К сожалению, такая команда доступна только в группах, '
                                                              'для проверки фото воспользуйтесь /test')
            except Exception as e:
                print(f'{e}')

    def test_handle_kick(self, mock_bot):
        """tests the work of /kick command"""
        message = MagicMock()
        if message.chat.type == 'supergroup':
            try:
                if message.reply_to_message:
                    message.chat.id = 12345
                    message.reply_to_message = MagicMock()
                    message.reply_to_message.from_user.id = 67890
                    message.reply_to_message.from_user.username = 'hihihi'
                    handle_kick(message)
                    mock_bot.kick_chat_member.assert_called_once()
                    call_args = mock_bot.kick_chat_member.call_args[1]
                    self.assertEqual(call_args['chat_id'], 12345)
                    self.assertEqual(call_args['user_id'], 67890)
                    mock_bot.send_message.assert_called_once_with(12345, f"Пользователь @hihihi был кикнут")
                else:
                    message.chat.id = 12345
                    handle_kick(message)
                    mock_bot.send_message.assert_called_once_with(12345,
                                                                  "Пожалуйста, ответьте на сообщение пользователя, которого надо кикнуть")
            except Exception as e:
                print(f'{e}')
        else:
            try:
                message.chat.id = 12345
                handle_kick(message)
                mock_bot.send_message.assert_called_once_with(12345,
                                                              'К сожалению, такая команда доступна только в группах, '
                                                              'для проверки фото воспользуйтесь /test')
            except Exception as e:
                print(f'{e}')

    def test_next_img(self, mock_bot):
        """tests the work of next_img function"""
        call = MagicMock()
        if call.chat.type == 'supergroup':
            return
        else:
            try:
                call.message.chat.id = 12345
                next_img(call)
                mock_bot.send_message.assert_called_once_with(12345,
                                                              "отправьте следующее фото:)")
            except Exception as e:
                print(f'{e}')


if __name__ == '__main__':
    unittest.main()
