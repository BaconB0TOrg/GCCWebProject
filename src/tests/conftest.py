import pytest
from app import app as main_app, db, tableModels as tm
from flask_login import FlaskLoginClient
from mc_lib.mcdocker import remove_docker, make_server

@pytest.fixture()
def app():
    main_app.config.update({
        "TESTING": True,
    })
    main_app.config['WTF_CSRF_ENABLED'] = False
    main_app.config['SESSION_PROTECTION '] = None
    main_app.test_client_class = FlaskLoginClient

    # other setup can go here

    yield main_app

    # clean up / reset resources here

@pytest.fixture()
def db_obj():
    yield db

@pytest.fixture()
def tableModelsSeededServers(app, docker_name):
    with app.app_context():
        tm.reset()
        remove_docker(docker_name)
        tm.seed_tests(server=True)
        
    yield tm

    # clean up / reset resources here
    with app.app_context():
        tm.reset()
        remove_docker(docker_name)

@pytest.fixture()
def tableModelsSeeded(app):
    with app.app_context():
        tm.reset()
        tm.seed_tests()
    
    yield tm

    # clean up / reset resources here
    with app.app_context():
        tm.reset()

@pytest.fixture()
def tableModels():
    yield tm

@pytest.fixture()
def client(app):
    yield app.test_client()

@pytest.fixture()
def client_with_user(app, tableModelsSeeded):
    with app.app_context():
        User = tableModelsSeeded.tables.User
        user = User.query.get(1)

    yield app.test_client(user=user)

@pytest.fixture()
def client_with_user_servers(app, tableModelsSeededServers):
    with app.app_context():
        User = tableModelsSeededServers.tables.User
        user = User.query.get(1)
    yield app.test_client(user=user)
        

@pytest.fixture()
def client_with_user_server(app, tableModelsSeededServers):
    with app.app_context():
        User = tableModelsSeededServers.tables.User
        user = User.query.get(1)

    yield app.test_client(user=user)


@pytest.fixture()
def runner(app):
    yield app.test_cli_runner()

@pytest.fixture()
def docker_name():
    yield "testName"

@pytest.fixture()
def cleanup_mc_server(app, db_obj, tableModels, docker_name):
    yield

    with app.app_context():
        server = tableModels.tables.Server.query.get(1)
        db_obj.session.delete(server)
        db_obj.session.commit()

    remove_docker(docker_name)

@pytest.fixture()
def create_mc_server(app, db_obj, tableModelsSeeded, docker_name):
    container_id = make_server(name=docker_name)
    with app.app_context():
        user = tableModelsSeeded.tables.User.query.get(1)
        server = tableModelsSeeded.tables.Server(name=docker_name, owner_id=user.id, port=25565, max_players=20, docker_id=container_id)
        db_obj.session.add(server)
        db_obj.session.commit()
        server = tableModelsSeeded.tables.Server.query.get(1)

    yield server