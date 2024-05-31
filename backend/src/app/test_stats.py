import unittest
from unittest.mock import patch

from flask import Flask

from app import app
from database import db, User, GroupStats


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch('database.draw_plot')
    @patch('database.draw_user_stats')
    @patch('database.plot_top_users')
    @patch('database.get_stats')
    def test_get_user_stats_not_found(self,
                                      mock_get_stats,
                                      mock_plot_top_users,
                                      mock_draw_user_stats,
                                      mock_draw_plot
                                      ):
        """Проверяет работу get_user_stats, когда статистика не найдена."""
        group_id = -123
        user_id = 123
        with app.app_context():
            user = User(user_id=user_id, group_id=group_id, username='test_user')
            db.session.add(user)
            group_stats = GroupStats(user_id=user_id, group_id=group_id, username='test_user')
            db.session.add(group_stats)
            db.session.commit()
            mock_get_stats.return_value = None
            mock_get_stats(user_id, group_id)
            mock_draw_user_stats(user_id, group_id)
            mock_plot_top_users(group_id, 5)
            mock_draw_plot(user_id, group_id)
        response = self.client.get(f'/stats/{group_id}/{user_id}')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, mock_get_stats.return_value)

        mock_get_stats.assert_called_once_with(user_id, group_id)
        mock_draw_user_stats.assert_called_once_with(user_id, group_id)
        mock_plot_top_users.assert_called_once_with(group_id, 5)
        mock_draw_plot.assert_called_once_with(user_id, group_id)

    @patch('database.draw_plot')
    @patch('database.draw_user_stats')
    @patch('database.plot_top_users')
    @patch('database.get_stats')
    def test_get_user_stats_found(self,
                                  mock_get_stats,
                                  mock_plot_top_users,
                                  mock_draw_user_stats,
                                  mock_draw_plot):
        """Проверяет работу get_user_stats, когда статистика найдена."""
        group_id = -123
        user_id = 2

        with app.app_context():
            user = User(user_id=user_id, group_id=group_id, username='kkk')
            db.session.add(user)
            group_stats = GroupStats(user_id=user_id, group_id=group_id, username='kkk')
            db.session.add(group_stats)
            db.session.commit()
            mock_get_stats.return_value = 200
            response = self.client.get(f'/stats/{group_id}/{user_id}')
            mock_get_stats(user_id, group_id)
            mock_draw_user_stats(user_id, group_id)
            mock_plot_top_users(group_id, 5)
            mock_draw_plot(group_id)
        mock_get_stats.assert_called_once_with(user_id, group_id)
        mock_draw_plot.assert_called_once_with(group_id)
        mock_draw_user_stats.assert_called_once_with(user_id, group_id)
        mock_plot_top_users.assert_called_once_with(group_id, 5)

    @patch('database.draw_plot')
    @patch('database.plot_top_users')
    def test_get_group_stats(self, mock_plot_top_users, mock_draw_plot):
        """Проверяет работу get_group_stats."""
        group_id = 123
        with app.app_context():
            user1 = User(user_id=1, group_id=group_id, username='user1')
            user2 = User(user_id=2, group_id=group_id, username='user2')
            group_stats1 = GroupStats(user_id=1, group_id=group_id, username='user1', count_nsfw_photos_sent=10)
            group_stats2 = GroupStats(user_id=2, group_id=group_id, username='user2', count_nsfw_photos_sent=5)
            db.session.add_all([user1, user2, group_stats1, group_stats2])
            db.session.commit()
            mock_draw_plot(group_id)
            mock_plot_top_users(group_id, 5)

        response = self.client.get(f'/group_stats/{group_id}')
        self.assertEqual(response.status_code, 404)
        mock_draw_plot.assert_called_once_with(group_id)
        mock_plot_top_users.assert_called_once_with(group_id, 5)


if __name__ == '__main__':
    unittest.main()
