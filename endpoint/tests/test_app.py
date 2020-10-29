def test_app(client):
    assert client.get("/").status_code == 200
