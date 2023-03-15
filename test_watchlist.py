import unittest
from urllib import response

from app import app, db, Movie, User

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

    def test_200_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)

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
        self.assertIn('Test Movie Title', data)
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
