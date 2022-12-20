import mc_lib.mcdocker as mcdocker

def test_mcdocker():
    server = mcdocker.make_server()
    assert server is not None