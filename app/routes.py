from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import get_db

main_bp = Blueprint("main", __name__)


def login_required(view):
    """Redirect to the login page if the user is not logged in."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped_view


@main_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("main.chat"))
    return redirect(url_for("main.login"))


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            return render_template("register.html", error="All fields are required.")

        if len(username) < 3:
            return render_template("register.html", error="Username must be at least 3 characters long.")

        if not username.replace("_", "").isalnum():
            return render_template("register.html", error="Username can only contain letters, numbers and underscores.")

        if len(password) < 4:
            return render_template("register.html", error="Password must be at least 4 characters long.")

        # Re-check the passwords match on the server too, since the
        # client-side JavaScript check can always be bypassed.
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()

        if existing is not None:
            return render_template("register.html", error="That username is already taken.")

        password_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        db.commit()

        return redirect(url_for("main.login", registered="1"))

    return render_template("register.html")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid username or password.")

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("main.chat"))

    just_registered = request.args.get("registered") == "1"
    return render_template("login.html", just_registered=just_registered)


@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@main_bp.route("/chat")
@login_required
def chat():
    return render_template(
        "chat.html",
        username=session["username"],
        user_id=session["user_id"],
    )


@main_bp.route("/users")
@login_required
def users():
    """Return every other registered user as JSON, for the sidebar list."""
    db = get_db()
    rows = db.execute(
        "SELECT id, username FROM users WHERE id != ? ORDER BY username COLLATE NOCASE",
        (session["user_id"],),
    ).fetchall()
    return jsonify([{"id": row["id"], "username": row["username"]} for row in rows])


@main_bp.route("/messages/<int:other_user_id>")
@login_required
def messages(other_user_id):
    """Return the chat history between the logged-in user and other_user_id."""
    db = get_db()
    my_id = session["user_id"]

    rows = db.execute(
        """
        SELECT sender_id, receiver_id, message, created_at
        FROM messages
        WHERE (sender_id = ? AND receiver_id = ?)
           OR (sender_id = ? AND receiver_id = ?)
        ORDER BY created_at ASC
        """,
        (my_id, other_user_id, other_user_id, my_id),
    ).fetchall()

    return jsonify(
        [
            {
                "sender_id": row["sender_id"],
                "receiver_id": row["receiver_id"],
                "message": row["message"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    )
