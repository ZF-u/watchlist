import unittest
from werkzeug import *

from app import app, db, Movie, User, forge, initdb

#测试继承unittest.TestCase继承类
class WatchlistTestCase(unittest.TestCase):

    # 固件测试 -------------------------------------------
    # setUp 准备好需要准备的内容
    def setUp(self):
        #更新配置
        app.config.update(
            # 测试模式 -> True
            TESTING=True,
            # 使用SQLite内存型数据库，不干扰开发使用的模拟数据库文件
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )

        db.create_all()

        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='Test Movie title', year='2023')

        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()  # create test client
        self.runner = app.test_cli_runner()  # create test runner
    
    # tearDown 打扫
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    # 测试程序是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    #----------------------------------------------------

    # 测试客户端 ------------------------------------------
    def test_404_page(self):
        response = self.client.get('/undefine')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    # def test_200_page(self):
    #     response = self.client.get('/')
    #     data = response.get_data(as_text=True)
    #     self.assertIn('Test\'s Watchlist', data)
    #     self.assertIn('Test Movie Title', data)
    #     self.assertEqual(response.status_code, 200)

    # 辅助方法，用于登录，follow_redirects=True跟随重定向，返回重定向后的相应
    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

    # test create
    def test_create_item(self):
        self.login()

        # 创建条目
        response = self.client.post('/', data=dict(
            title="New Movie",
            year='2023'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)
        self.assertIn('New Movie', data)

        # 创建条目，但标题为空
        response = self.client.post('/', data=dict(
            title='',
            year='2023'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input', data)

        # 创建条目，但年份为空
        response = self.client.post('/', data=dict(
            title='New Movie',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input', data)

    # test update
    def test_update_item(self):
        self.login()

        # edit
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Test Movie title', data)
        self.assertIn('2023', data)

        # update
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year='2023'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.', data)
        self.assertIn('New Movie Edited', data)

        # update but title null
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2023'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.', data)
        self.assertIn('Invalid input', data)

        # update but year null
        response = self.client.post('mocie/edit/1', data=dict(
            title='New Movie Edited',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.', data)
        self.assertIn('Invalid input', data)

    # test delete
    def test_delete_item(self):
        self.login()

        response = self.client.post('movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie Title', data)

    # test login ptk
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)

    # test login
    def test_login(self):
        response = self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)

        # wrong pw
        response = self.client.post('/login', data=dict(
            username='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # wrogn usr
        response = self.client.post('/login', data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # null usr
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

        # null pwd
        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

    # test logout
    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Bye.', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('<form method="post">', data)

    # test setting
    def test_settings(self):
        self.login()

        # test setting page
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Your Name', data)

        # test setting update
        response = self.client.post('/settings', data=dict(
            name='NoctEee'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated.', data)
        self.assertIn('NoctEee', data)

        # test updat but null name
        response = self.client.post('/settings', data=dict(
            name=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated.', data)
        self.assertIn('Invalid input.', data)

    # test mock data
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done.', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    # test initdb
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    # test gen admin account
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username', 'grey', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'grey')
        self.assertTrue(User.query.first().validate_password('123'))

    # test updat admin
    def test_admin_command_update(self):
        result = self.runner.invoke(args=['admin', '--username', 'peter', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'peter')
        self.assertTrue(User.query.first().validate_password('456'))

if __name__ == '__main__':
    with app.app_context():
        unittest.main()