import os

from flask import Flask
from flask_socketio import SocketIO

from app.database import init_db, close_db

# Created once, initialised onto the Flask app inside create_app().
# threading async_mode is used because it works everywhere (local dev,
# and gunicorn with the gthread worker class on Render) without needing
# any extra system packages like eventlet/gevent.
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")


def create_app():
    """Application factory: builds and configures the Flask app."""
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # SECRET_KEY is read from the environment. A fallback is provided so the
    # app still runs locally the very first time, but on Render you MUST
    # set a real SECRET_KEY environment variable (see README).
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-me-before-deploying"
    )

    # Database lives in instance/chat.db
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    instance_path = os.path.join(basedir, "instance")
    os.makedirs(instance_path, exist_ok=True)
    app.config["DATABASE"] = os.path.join(instance_path, "chat.db")

    # Create tables if they do not exist yet.
    init_db(app.config["DATABASE"])

    # Make sure the per-request SQLite connection is closed properly.
    app.teardown_appcontext(close_db)

    # Register HTTP routes.
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Attach Socket.IO to this Flask app.
    socketio.init_app(app)

    # Import socket event handlers so their @socketio.on(...) decorators run.
    from app import socket_events  # noqa: F401

    return app
