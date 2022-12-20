import mc_lib.mcdocker as mcdocker

def test_mcdocker():
    server = mcdocker.make_server(threaded=False)
    assert server is not None

def test_change_server_props():
    assert mcdocker.update_server_properties(updated_properties={"difficulty":"hard"}) == True

