import pytest
from app import app as main_app
import mc_lib.mcdocker as mcdocker

@pytest.fixture()
def app():
    main_app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield main_app

    # clean up / reset resources here

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture(scope="session")
def setup_docker(request):
    print("Setting Docker Env")
    server = mcdocker.make_server(threaded=False) # Force a linear run through
    def teardown():
        print("Teardown Docker Env")
        mcdocker.remove_docker(container_id=server) == False # True meaning it return successfully
    request.addfinalizer(teardown)
    return {
        "server_name": server,
    } 