import mc_lib.mcdocker as mcdocker
import pytest

def test_server_creation(setup_docker):
    """Makes sure the server was generated"""
    assert setup_docker["server_name"] is not None

def test_change_server_props(setup_docker):
    """Makes sure that the server config can be changed after creation"""
    assert mcdocker.update_server_properties(container_id= setup_docker["server_name"], updated_properties={"difficulty":"hard"}) == True

def test_rcon(setup_docker):
    """RCON command to mc-server are configured correctly"""
    assert mcdocker.run_docker_mc_command(container_id=None) is None
    """Assert that the function works, checks to make sure nothing is raised"""
    assert mcdocker.run_docker_mc_command(container_id=setup_docker["server_name"], message="list")
    """Assert that the function works with no message"""
    assert mcdocker.run_docker_mc_command(container_id=setup_docker["server_name"])

def test_delete_docker_none(setup_docker):
    """Control flow on setup_docker with nothing for the container id"""
    assert mcdocker.remove_docker(container_id=None) is None

def test_control_docker(setup_docker):
    """Control flow on the start and stop docker calls"""
    assert mcdocker.start_docker(container_id=None) is None
    assert mcdocker.stop_docker(container_id=None) is None
    assert mcdocker.stop_docker(container_id=setup_docker["server_name"]) == True
    assert mcdocker.start_docker(container_id=setup_docker["server_name"]) == True
