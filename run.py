import os

from app import create_app, socketio

# This module-level "app" is what Gunicorn runs in production
# (see the Procfile: "run:app").
app = create_app()

if __name__ == "__main__":
    # Local development entry point: `python run.py`
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
