import os
import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_index_default_message(client):
    os.environ.pop("MESSAGE", None)
    rv = client.get("/")
    assert rv.status_code == 200
    assert rv.get_json() == {"message": "Hello"}


def test_index_custom_message(client, monkeypatch):
    monkeypatch.setenv("MESSAGE", "Hi there")
    rv = client.get("/")
    assert rv.status_code == 200
    assert rv.get_json() == {"message": "Hi there"}


def test_health(client):
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.get_json() == {"status": "healthy"}


# negative test case for invalid route
def test_invalid_route(client):
    rv = client.get("/invalid")
    assert rv.status_code == 404


def test_index_empty_message(client, monkeypatch):
    monkeypatch.setenv("MESSAGE", "")
    rv = client.get("/")
    assert rv.status_code == 200
    assert rv.get_json() == {"message": ""}


# edge case: very long message
def test_index_long_message(client, monkeypatch):
    long_message = "A" * 1000
    monkeypatch.setenv("MESSAGE", long_message)
    rv = client.get("/")
    assert rv.status_code == 200
    assert rv.get_json() == {"message": long_message}


def test_index_special_characters(client, monkeypatch):
    special_message = "!@#$%^&*()_+"
    monkeypatch.setenv("MESSAGE", special_message)
    rv = client.get("/")
    assert rv.status_code == 200
    assert rv.get_json() == {"message": special_message}


def test_index_unicode_message(client, monkeypatch):
    unicode_message = "こんにちは"
    monkeypatch.setenv("MESSAGE", unicode_message)
    rv = client.get("/")
    assert rv.status_code == 200
    assert rv.get_json() == {"message": unicode_message}
