def test_request_example(client):
    response = client.get("/welcome/")
    assert b'<h1 class="display-3">Minecraft Server Hosting</h1>' in response.data