def test_request_example(client):
    response = client.get("/welcome/")
    assert b"<h2>Featured Servers</h2>" in response.data