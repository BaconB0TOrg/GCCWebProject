import mc_lib.mcdocker as mcdocker

def test_mcdocker():
    """Makes sure that the docker mc server can still be deployed"""
    server = mcdocker.make_server(threaded=False)
    assert server is not None

def test_change_server_props():
    """Makes sure that the server config can be changed after creation"""
    assert mcdocker.update_server_properties(updated_properties={"difficulty":"hard"}) == True

def test_rcon():
    """RCON command to mc-server are configured correctly"""
    pass