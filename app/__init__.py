import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()


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

    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    db.init_app(app)
    socketio.init_app(app)

    init_routes(app)
    init_api(app)
    init_sockets(socketio)

    with app.app_context():
        db.create_all()

    return app