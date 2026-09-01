from flask import session
from flask_socketio import join_room, emit, disconnect

from app import socketio
from app.database import get_db

# Simple in-memory record of who is currently online: {user_id: username}
# This is fine for a single-process student/internship deployment.
online_users = {}


def user_room(user_id):
    """Every user has their own private Socket.IO room, e.g. 'user_101'."""
    return f"user_{user_id}"


@socketio.on("connect")
def handle_connect():
    if "user_id" not in session:
        # Someone tried to open a socket without being logged in.
        disconnect()
        return

    user_id = session["user_id"]
    username = session["username"]

    join_room(user_room(user_id))
    online_users[user_id] = username

    emit("online_users", list(online_users.keys()), broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    user_id = session.get("user_id")
    if user_id is not None and user_id in online_users:
        del online_users[user_id]
        emit("online_users", list(online_users.keys()), broadcast=True)


@socketio.on("send_message")
def handle_send_message(data):
    if "user_id" not in session:
        return

    sender_id = session["user_id"]
    receiver_id = data.get("receiver_id")
    message = (data.get("message") or "").strip()

    if not receiver_id:
        emit("message_error", {"error": "No receiver selected."})
        return

    if not message:
        emit("message_error", {"error": "Message cannot be empty."})
        return

    db = get_db()
    receiver = db.execute(
        "SELECT id FROM users WHERE id = ?", (receiver_id,)
    ).fetchone()

    if receiver is None:
        emit("message_error", {"error": "That user does not exist."})
        return

    cursor = db.execute(
        "INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)",
        (sender_id, receiver_id, message),
    )
    db.commit()

    row = db.execute(
        "SELECT id, sender_id, receiver_id, message, created_at FROM messages WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()

    payload = {
        "id": row["id"],
        "sender_id": row["sender_id"],
        "receiver_id": row["receiver_id"],
        "message": row["message"],
        "created_at": row["created_at"],
    }

    # Send to the receiver's room and back to the sender's own room
    # (so the sender's other open tabs also see the message).
    emit("receive_message", payload, room=user_room(receiver_id))
    emit("receive_message", payload, room=user_room(sender_id))


@socketio.on("typing")
def handle_typing(data):
    if "user_id" not in session:
        return
    receiver_id = data.get("receiver_id")
    if not receiver_id:
        return
    emit(
        "typing",
        {"sender_id": session["user_id"], "username": session["username"]},
        room=user_room(receiver_id),
    )


@socketio.on("stop_typing")
def handle_stop_typing(data):
    if "user_id" not in session:
        return
    receiver_id = data.get("receiver_id")
    if not receiver_id:
        return
    emit(
        "stop_typing",
        {"sender_id": session["user_id"]},
        room=user_room(receiver_id),
    )
