import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_socketio import SocketIO
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
socketio = SocketIO()
oauth = OAuth()


def create_app():
    from app.routes import init_routes
    from app.api import init_api
    from app.sockets import init_sockets
    from app import models

    app = Flask(__name__)

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    app.config["SECRET_KEY"] = "dev-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wordlearner.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "media")

    app.config["GITHUB_CLIENT_ID"] = os.getenv("GITHUB_CLIENT_ID")
    app.config["GITHUB_CLIENT_SECRET"] = os.getenv("GITHUB_CLIENT_SECRET")
    app.config["YANDEX_CLIENT_ID"] = os.getenv("YANDEX_CLIENT_ID")
    app.config["YANDEX_CLIENT_SECRET"] = os.getenv("YANDEX_CLIENT_SECRET")

    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    db.init_app(app)
    socketio.init_app(app)
    oauth.init_app(app)

    oauth.register(
        name="github",
        client_id=app.config["GITHUB_CLIENT_ID"],
        client_secret=app.config["GITHUB_CLIENT_SECRET"],
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )

    oauth.register(
        name="yandex",
        client_id=app.config["YANDEX_CLIENT_ID"],
        client_secret=app.config["YANDEX_CLIENT_SECRET"],
        access_token_url="https://oauth.yandex.com/token",
        authorize_url="https://oauth.yandex.com/authorize",
        api_base_url="https://login.yandex.ru/",
        client_kwargs={"scope": "login:email login:info"},
    )

    init_routes(app)
    init_api(app)
    init_sockets(socketio)

    with app.app_context():
        db.create_all()

    return app