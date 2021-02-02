import os


def test_app(client):
    assert client.get("/").status_code == 200
    assert client.get("/healthz").status_code == 200
    assert client.get("/readiness").status_code == 200
    assert client.get("/" + os.environ["ENDPOINT_PATH"]).status_code == 200

    assert client.get("/not_existing_name").status_code == 404
