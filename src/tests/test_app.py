from flask import Flask
from app import db
import models

####### GET ROUTES #############
def test_redirect_to_welcome(client):
    response = client.get('/', follow_redirects=True)
    assert len(response.history) == 1

def test_welcome(client):
    response = client.get('/welcome/')
    assert b'Minecraft Server Hosting' in response.data

def test_get_logout_anon(client):
    response = client.get('/logout/', follow_redirects=True)
    assert len(response.history) == 1           ,"/logout/ should redirect" 
    assert response.request.path == '/welcome/' ,'/logout/ should redirect to /welcome/ when no next parameter is specified'

# def test_get_logout_auth(client):
#     with client:
#         with client.session_transaction() as session:
#         response = client.get('/logout/', follow_redirects=True)
#         assert len(response.history) == 1,          "/logout/ should redirect"
#         assert response.request.path == '/welcome/','/logout/ should redirect to /welcome/'

# def test_get_login(client):
#     with client:
#         response = client.get('/login/')
#         assert b'Log in' in response.data,       "'Log in' should be present on the page."

def test_get_register(client):
    response = client.get('/register/')
    assert b'Sign up' in response.data


####### POST ROUTES #############


# Account Tests that depend on DB #
# class AccountDbTest(TestCase):
#     SQLALCHEMY_DATABASE_URI = "sqlite://"
#     TESTING = True
#     User = Server = Tag = SiteRole = ServerTag = ServerRolePermission = UserServerRole = ServerEvent = None

#     def create_app(self):
#         app = Flask(__name__)
#         app.config['TESTING'] = True
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
#         self.User, self.Server, self.Tag, self.SiteRole, self.ServerTag, self.ServerRolePermission, self.UserServerRole, self.ServerEvent = models.setup_models(db)
#         return app

#     def setUp(self):
#         db.create_all()
        
#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()

#     def test_post_login_fail(self, client):
#         data = {
#             'username': 'test',
#             'password': 'password'
#         }
#         response = client.post('/login/', data=data, follow_redirects=True)
#         assert response.status_code == 400

#     def test_post_login_succeed(self, client):
#         user = self.User(password='password', email='test@test.com', username='test')
#         db.session.add(user)
#         db.session.commit()

#         data = {
#             'username': 'test',
#             'password': 'password'
#         }
#         response = client.post('/login/', data=data, follow_redirects=True)
#         assert response.status_code == 200


