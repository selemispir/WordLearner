import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pytest

from app import create_app, db
from app.models import User, Word, Category
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()

        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("123456")
        )
        db.session.add(user)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client):
    return client.post("/login", data={
        "email": "test@example.com",
        "password": "123456"
    }, follow_redirects=True)


def test_home_page(client):
    response = client.get("/")
    assert b"WordLearner" in response.data


def test_login_success(client):
    response = login(client)
    assert b"Login successful" in response.data


def test_words_requires_login(client):
    response = client.get("/words", follow_redirects=True)
    assert b"Please log in first" in response.data


def test_add_word(client):
    login(client)

    response = client.post("/words/add", data={
        "english": "book",
        "russian": "книга",
        "example_sentence": "I read a book."
    }, follow_redirects=True)

    assert b"Word added successfully" in response.data
    assert b"book" in response.data


def test_api_categories(client, app):
    with app.app_context():
        category = Category(name="Test Category")
        db.session.add(category)
        db.session.commit()

    response = client.get("/api/categories")
    assert response.status_code == 200
    assert b"Test Category" in response.data