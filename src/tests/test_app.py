import pytest
from flask_login import current_user, login_user
import mc_lib.mcdocker as mcdocker
from mc_lib.mcdocker import remove_docker

# TODO: Test these routes:
# - change_email
# - get_terminal
# - mc_command

############# GET ROUTES #############

def test_redirect_to_welcome(client):
    response = client.get('/', follow_redirects=True)
    assert len(response.history) == 1
    assert response.request.path == '/welcome/' ,'/ should redirect to /welcome/'

def test_welcome(client):
    response = client.get('/welcome/')
    assert b'Minecraft Server Hosting' in response.data

def test_get_logout_anon(client):
    response = client.get('/logout/', follow_redirects=True)
    assert len(response.history) == 1           ,"/logout/ should redirect" 
    assert response.request.path == '/welcome/' ,'/logout/ should redirect to /welcome/ when no next parameter is specified'

def test_get_logout_auth(client_with_user):
    with client_with_user as client:
        response = client.get('/logout/', follow_redirects=True)
        assert len(response.history) == 1,          "Redirects once."
        assert response.request.path == '/welcome/','/logout/ should redirect to /welcome/'

def test_get_login(client):
    with client:
        response = client.get('/login/')
        assert b'Log in' in response.data, "'Log in' should be present on the page."

def test_get_register(client):
    response = client.get('/register/')
    assert b'Sign up' in response.data

def test_list_server_anon(client):
    with client:
        response = client.get('/servers/')
        assert b'All Servers' in response.data
        # TODO: Maybe test that the correct number of servers are shown?
    response = client.get('/register/')
    assert b'Sign up' in response.data

def test_list_server_auth(client_with_user):
    with client_with_user as client:
        response = client.get('/servers/')
        assert b'All Servers' in response.data
        # TODO: Maybe test that the correct number of servers are shown?

def test_get_create_server_anon(client):
    with client:
        response = client.get('/servers/create/', follow_redirects=True)
        assert response.request.path == '/login/', 'Anonymous users are redirected to login'

def test_get_create_server_auth(client_with_user):
    with client_with_user as client:
        response = client.get('/servers/create/')
        assert b'Create a new Server' \
            in response.data, 'Authenticated users can access the create server form.'
        # TODO: Maybe test that all the tags are present?

def test_show_server_anon(app, client, tableModelsSeededServers):
    with client:
        with app.app_context():
            server = tableModelsSeededServers.tables.Server.query.get(1)
        response = client.get(f'/servers/{server.id}/')
        assert b'testName' in response.data, "Show the right server's information."

def test_show_server_auth(app, client_with_user_servers, tableModels):
    with app.app_context():
        server = tableModels.tables.Server.query.get(1)
    with client_with_user_servers as client:
        response = client.get(f'/servers/{server.id}/')
        assert b'testName' in response.data, "Show the right server's information."

def test_get_update_server_anon(client, tableModelsSeededServers):
    with client:
        response = client.get('/servers/1/update/', follow_redirects=True)
        assert b'Log in' in response.data,          "The login page is shown"
        assert response.request.path == '/login/',   "Anonymous users are redirected to login."

def test_get_update_server_auth_owner(client_with_user_servers):
    with client_with_user_servers as client:
        response = client.get('/servers/1/update/')
        assert b'Update Server' in response.data, "Shows the update page for the server"

def test_get_update_server_auth_bad_user(app, db_obj, tableModelsSeededServers):
    with app.app_context():
        User = tableModelsSeededServers.tables.User
        user = User(username='newUser', password='password', email='new@user.com')
        db_obj.session.add(user)
        db_obj.session.commit()
        with app.test_client(user=user) as client:
            response = client.get('/servers/1/update/', follow_redirects=True)
            assert len(response.history) == 1,          "Redirects once."
            assert response.request.path == '/servers/', "Only owners of the server can view the update server form."

def test_get_update_server_auth_bad_server(client_with_user_servers):
    with client_with_user_servers as client:
        response = client.get('/servers/2/update/', follow_redirects=True)
        assert len(response.history) == 1,          "Redirects once."
        assert response.request.path == '/servers/', "Redirects to list servers page"

def test_delete_server(app, create_mc_server, tableModels):
    server = create_mc_server
    with app.app_context():
        user = tableModels.tables.User.query.get(1)
        with app.test_client(user=user) as client:
            response = client.get('/servers/1/delete/', follow_redirects=True)
            assert len(response.history) == 1,              "Redirects once."
            assert response.request.path == '/servers/',     "Redirects to the list servers page."
            assert remove_docker(server.docker_id) == False,"Docker container is deleted."
            no_server = tableModels.tables.Server.query.get(1)
            assert no_server == None,                       "Server is deleted from db."

############# POST ROUTES #############


def test_post_login_no_user(client):
    with client:
        response = client.post('/login/', follow_redirects=True, data={
            'username': 'testUser',
            'password': 'password'
        })
        assert len(response.history) == 1, "Redirects once"
        assert b'Log in' in response.data, "'Log in' should be present on the page."

def test_post_login_succeed(client, tableModelsSeeded):
    with client:
        response = client.post('/login/', follow_redirects=True, data={
            'username': 'test',
            'password': 'password'
        })
        assert len(response.history) == 1
        assert b'Minecraft Server Hosting' in response.data, "Successfull logins go to /welcome/"

def test_post_login_when_logged_in(client_with_user):
    with client_with_user as client:
        response = client.post('/login/', follow_redirects=True, data={
            'username': 'test',
            'password': 'password'
        })
        assert response.request.path == '/welcome/', "Posting to /login/ should redirect to /welcome/ if already logged in and when the 'next' argument is not specified"
        assert b'Minecraft Server Hosting' in response.data

def test_post_register_new(client, tableModels):
    with client:
        response = client.post('/register/', follow_redirects=True, data=dict(
            username='test',
            password='password',
            confirm_password='password',
            email="test@test.com",
            confirm_email='test@test.com'
        ))
        assert len(response.history) == 1
        assert response.request.path == '/welcome/', "Successfully registering redirects to /welcome/"
        user = tableModels.tables.User.query.get(1)
        login_user(user)
        assert current_user.username == 'test'

def test_post_register_fail_exists(app, client, tableModelsSeeded):
    with client:
        response = client.post('/register/', follow_redirects=True, data=dict(
            username='test',
            password='password',
            confirm_password='password',
            email="test@test.com",
            confirm_email='test@test.com'
        ))
        assert len(response.history) == 1
        assert response.request.path == '/register/', "Failing to register redirects back to /register/"

def test_post_register_fail_form(client):
    with client:
        response = client.post('/register/', follow_redirects=True, data=dict(
            username='test',
            password='password',
            confirm_password='NOTTHESAME',
            email="test@test.com",
            confirm_email='test@test.com'
        ))
        assert len(response.history) == 1
        assert response.request.path == '/register/', "Failing to register redirects back to /register/"

def test_post_create_server_anon(app, tableModels, client, docker_name):
    with client:
        response = client.post('/servers/create/', follow_redirects=True, data=dict(
            server_name=docker_name,
            server_description="Test Server Description",
            tags=[],
            number_of_players=20,
            gamemode='survival',
            difficulty='peaceful'
        ))
        with app.app_context():
            servers = tableModels.tables.Server.query.all()
            assert len(servers) == 0
        assert response.request.path == '/login/', 'Anonymous users are redirected to login'

def test_post_create_server_auth_succeed(app, tableModels, client_with_user, cleanup_mc_server, docker_name):
    with client_with_user as client:
        response = client.post('/servers/create/', follow_redirects=True, data=dict(
            server_name=docker_name,
            server_description="Test Server Description",
            tags=[],
            number_of_players=20,
            gamemode='survival',
            difficulty='peaceful'
        ))
        assert len(response.history) == 1,          "Redirects once."
        assert response.request.path == '/servers/', "Redirected to page listing all servers."
        with app.app_context():
            servers = tableModels.tables.Server.query.all()
            assert len(servers) == 1,               "Server object is created and saved."
        assert b'All Servers' in response.data

def test_post_create_server_auth_fail(client_with_user):
    with client_with_user as client:
        response = client.post('/servers/create/', follow_redirects=True, data=dict(
            server_name='',
            server_description="Test Server Description",
            tags=[],
            number_of_players=20,
            gamemode='survival',
            difficulty='peaceful'
        ))
        assert len(response.history) == 1
        assert response.request.path == '/servers/create/'
        assert b'Create a new Server' in response.data

def test_post_update_server_anon(client, tableModelsSeededServers):
    with client:
        response = client.post('/servers/1/update/', follow_redirects=True, data=dict(
            name="NewName",
            description="New Description",
            tags=[4, 5],
            id=1
        ))
        assert len(response.history) == 1,          "Redirects Twice: to "
        assert response.request.path == '/login/',  "Redirects anonymous users to login page."

def test_post_update_server_auth_owner(app, client_with_user_servers, tableModels):
    with client_with_user_servers as client:
        response = client.post('/servers/1/update/', follow_redirects=True, data=dict(
            name="NewName",
            description="New Description",
            tags=[4, 5],
            id=1
        ))
        assert len(response.history) == 1,              "Redirects once."
        assert response.request.path == '/servers/1/',   "Redirects to the correct path"
        assert b'NewName' in response.data,             "The correct server's page is shown."

def test_post_update_server_auth_bad_user(app, db_obj, tableModelsSeededServers):
    with app.app_context():
        User = tableModelsSeededServers.tables.User
        user = User(username="newUser", password='password', email='new@user.com')
        db_obj.session.add(user)
        db_obj.session.commit()
        with app.test_client(user=user) as client:
            response = client.post('/servers/1/update/', follow_redirects=True, data=dict(
                name="NewName",
                description="New Description",
                tags=[4, 5],
                id=1
            ))
            assert len(response.history) == 1,                  "Redirects once."
            assert response.request.path == '/servers/create/',   "Redirects to the create server page."
            Server = tableModelsSeededServers.tables.Server
            server = Server.query.get(1)
            assert server.name == 'testName',                   "Server's information is not changed."
