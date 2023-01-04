from flask import session

####### GET ROUTES #############
def test_redirect_to_welcome(client):
    response = client.get("/", follow_redirects=True)
    assert len(response.history) == 1

def test_welcome(client):
    response = client.get("/welcome/")
    assert b'<h1 class="display-3">Minecraft Server Hosting</h1>' in response.data

def test_get_logout(client):
    with client:
        response = client.get("/logout/")
        assert len(response.history) == 1
        assert session['logged-in'] == False
        assert session['user-email'] == None
        assert session['user-id'] == None
        assert b'<h1 class="display-3">Minecraft Server Hosting</h1>' in response.data
    with client.session_transaction() as session:
        session['user-id'] = 1
        session['logged-in'] = True
        session['user-email'] = 

def test_get_login(client):
    with client:
        response = client.get("/login/")
        assert session['logged-in'] != False
        assert session['user-email'] != None
        assert session['user-id'] != None
        assert b'Log in' in response.data

def test_get_register(client):
    response = client.get("/register/")
    assert b'Sign up' in response.data


####### POST ROUTES #############

def test_post_a_route(client):
    data = {
        'field1': 'data1'
    }
    response = client.post('/a/', data=data)
    assert response.status_code == 200
