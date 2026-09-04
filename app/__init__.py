import os

from flask import Flask
from flask_socketio import SocketIO

from app.database import init_db, close_db

# Socket.IO configuration
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading"
)


def create_app():
    """Application factory: builds and configures the Flask app."""

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # SECRET_KEY
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-me-before-deploying"
    )

    # Database path for Vercel's temporary writable directory
    app.config["DATABASE"] = "/tmp/chat.db"

    # Create database tables
    init_db(app.config["DATABASE"])

    # Close database connection after each request
    app.teardown_appcontext(close_db)

    # Register HTTP routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Attach Socket.IO
    socketio.init_app(app)

    # Import Socket.IO event handlers
    from app import socket_events  # noqa: F401

    return app