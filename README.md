# Real-Time Communication App

A one-to-one real-time chat application built with **Flask**,
**Flask-SocketIO**, and **SQLite**. Users register and log in with just
a **username and password** — no phone number, no OTP, no email
verification, and no paid third-party services. Once logged in, a user
can search for and select any other registered user and chat with them
instantly, with no page refresh.

This project is designed and documented as a college/internship-level
software project: a simple, well-understood technology stack, clean
code, and complete documentation.

---

## Table of Contents

1. Project Overview
2. Problem Statement
3. Objectives
4. Features
5. Technologies Used
6. System Architecture
7. Project Structure
8. Database Design
9. Installation
10. Local Execution
11. Testing
12. GitHub Deployment
13. Render Deployment
14. Environment Variables
15. Security
16. Limitations
17. Future Enhancements
18. Conclusion
19. Simple Concept Explanations
20. Real-Time Message Flow
21. Common Errors and Solutions
22. Internship Presentation Content
23. Viva Questions and Answers

---

## 1. Project Overview

**Real-Time Communication App** is a web-based chat application that
lets registered users exchange text messages with each other instantly.
Unlike many chat demos that rely on a phone number and an OTP (One-Time
Password) service, this project authenticates users with only a
username and a password, which keeps the project free to build, free
to run, and free of any third-party paid service.

## 2. Problem Statement

Most real-world chat systems require a phone number, email
verification, or a paid messaging/SMS API to identify users. For a
student project, this adds unnecessary cost and complexity, and it
depends on external services that may not always be available or
free. There is a need for a **simple, self-contained, real-time chat
system** that can be built, run, and demonstrated entirely with free
and open technologies.

## 3. Objectives

- Allow users to register and log in using only a username and password.
- Allow any logged-in user to message any other registered user.
- Deliver messages **instantly**, without the receiver refreshing the page.
- Store all users and messages persistently in a database.
- Show whether a user is currently online or offline.
- Show a "typing..." indicator while the other person is composing a message.
- Keep the entire stack free to build and free to deploy.

## 4. Features

1. User registration (username + password, with confirm-password check)
2. User login
3. User logout
4. Username/password authentication using Flask sessions
5. Password hashing (passwords are never stored in plain text)
6. Full list of all registered users
7. Live search/filter of the user list
8. One-to-one private chat
9. Real-time messaging over Socket.IO (no polling, no refresh)
10. Persistent chat history, reloaded from the database
11. Online status indicator
12. Offline status indicator
13. Typing indicator
14. Message timestamps
15. Empty-message validation
16. Invalid login handling (clear error message, no crash)
17. Duplicate-username handling at registration
18. Secure server-side session handling
19. Fully responsive design (desktop, laptop, tablet, mobile)
20. Professional, modern UI (not a bare HTML demo)
21. Centralized error handling and user-facing error messages
22. SQLite-backed persistent storage

## 5. Technologies Used

| Layer          | Technology                                   | Why |
|----------------|-----------------------------------------------|-----|
| Frontend       | HTML5, CSS3, vanilla JavaScript               | No build tools needed, easy for a beginner to read and modify |
| Backend        | Python 3, Flask                               | Lightweight, widely taught, quick to set up |
| Real-time      | Flask-SocketIO, Socket.IO (client)            | Provides a persistent, bidirectional connection so the server can push messages instantly |
| Database       | SQLite                                        | Zero-configuration, file-based, perfect for a student project |
| Authentication | Flask sessions + Werkzeug password hashing    | Built into Flask/Werkzeug, no extra dependency needed |
| Server         | Gunicorn (`gthread` worker)                   | Production-grade WSGI server, works with Flask-SocketIO's threading mode |
| Deployment     | GitHub + Render (Free Web Service)            | Free, beginner-friendly, integrates directly with GitHub |

No paid API (OpenAI, Gemini, Twilio, Firebase, etc.) and no credit card
are required anywhere in this project.

## 6. System Architecture

```
+-------------------+        HTTP (login/register/pages)        +--------------------+
|                    |  ----------------------------------->     |                    |
|   User A Browser   |                                            |   Flask Server     |
|  (HTML/CSS/JS +    |        Socket.IO (real-time events)        |  (Flask-SocketIO)  |
|   Socket.IO client)| <----------------------------------->      |                    |
|                    |                                            +---------+----------+
+--------------------+                                                      |
                                                                             | SQL (parameterized)
                                                                             v
                                                                    +-------------------+
                                                                    |   SQLite Database  |
                                                                    |  (users, messages) |
                                                                    +-------------------+
                                                                             ^
                                                                             |
+--------------------+        HTTP + Socket.IO                              |
|   User B Browser   | <---------------------------------------------------+
+--------------------+
```

- **HTTP routes** (`/register`, `/login`, `/logout`, `/users`,
  `/messages/<id>`) handle authentication and loading data.
- **Socket.IO** handles everything that must happen instantly: sending a
  message, showing who is online, and typing indicators.
- **SQLite** is the single source of truth for user accounts and chat
  history.

### Modules

1. **Authentication Module** — registration, login, logout, password hashing, session management.
2. **User Management Module** — listing and searching registered users.
3. **Real-Time Messaging Module** — Socket.IO events for sending and receiving messages.
4. **Presence Module** — tracking and broadcasting who is online/offline.
5. **Chat History Module** — storing and retrieving past conversations.
6. **Database Module** — SQLite connection handling and schema creation.

## 7. Project Structure

```
Real_Time_Communication_App/
│
├── app/
│   ├── __init__.py        # Flask app factory: config, DB init, blueprint & Socket.IO setup
│   ├── database.py        # SQLite connection handling + table creation
│   ├── routes.py          # HTTP routes: register, login, logout, users, messages
│   └── socket_events.py   # Socket.IO events: connect, disconnect, send_message, typing
│
├── templates/
│   ├── base.html          # Shared HTML shell
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   └── chat.html          # Main chat interface
│
├── static/
│   ├── css/
│   │   └── style.css      # All styling (professional UI + responsive layout)
│   └── js/
│       └── script.js      # Socket.IO client logic: users, messages, typing, search
│
├── instance/
│   └── .gitkeep            # chat.db (SQLite file) is created here automatically at runtime
│
├── run.py                  # Application entry point (local + Gunicorn)
├── requirements.txt        # Python dependencies
├── Procfile                 # Tells Render how to start the app in production
├── .gitignore
├── .env.example
└── README.md
```

## 8. Database Design

**Database file:** `instance/chat.db` (SQLite)

### `users` table

| Column         | Type     | Notes                              |
|----------------|----------|-------------------------------------|
| id             | INTEGER  | Primary key, auto-increment         |
| username       | TEXT     | Unique, not null                    |
| password_hash  | TEXT     | Hashed with Werkzeug, never plain text |
| created_at     | TIMESTAMP| Defaults to the current time        |

### `messages` table

| Column       | Type      | Notes                                   |
|--------------|-----------|-------------------------------------------|
| id           | INTEGER   | Primary key, auto-increment                |
| sender_id    | INTEGER   | Foreign key → `users.id`                   |
| receiver_id  | INTEGER   | Foreign key → `users.id`                   |
| message      | TEXT      | The message text                           |
| created_at   | TIMESTAMP | Defaults to the current time               |

An index on `(sender_id, receiver_id)` speeds up loading a conversation
between two specific users. All queries use **parameterized SQL** (`?`
placeholders) to prevent SQL injection.

---

## 9. Installation

### Requirements

- Python 3.10 or newer
- pip (comes with Python)
- Git (for GitHub deployment)
- A free GitHub account and a free Render account (for deployment)

### Clone or download the project, then continue with Local Execution below.

## 10. Local Execution (Windows)

### Step 1 — Create and activate a virtual environment

**PowerShell:**
```powershell
py -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

**If PowerShell activation doesn't work, use Command Prompt (CMD):**
```cmd
py -m venv venv
venv\Scripts\activate.bat
```

### Step 2 — Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 3 — Set your SECRET_KEY for this terminal session

**PowerShell:**
```powershell
$env:SECRET_KEY="replace-this-with-a-long-secret"
```

**CMD:**
```cmd
set SECRET_KEY=replace-this-with-a-long-secret
```

### Step 4 — Run the app

```powershell
python run.py
```

### Step 5 — Open it in your browser

```
http://127.0.0.1:5000
```

---

## 11. Testing

**Step 1.** Open Chrome and go to `/register`.
Register:
```
Username: kavi123
Password: kavi1234
```

**Step 2.** Open a second, separate browser session (a different browser,
or an incognito/private window) and register:
```
Username: priya123
Password: priya1234
```

**Step 3.** In the first window, log in as `kavi123`.

**Step 4.** Select `priya123` from the sidebar (try the search box too).

**Step 5.** Send: `Hello Priya`

**Step 6.** In the second window, log in as `priya123`. The message
`Hello Priya` should already be there, and any new message sent while
both are logged in should appear **instantly**, with no refresh.

### Full checklist to test

- [ ] Reply back and forth between both accounts
- [ ] Typing indicator appears on the other side while typing, and disappears after a pause
- [ ] Online dot is green while both users are connected
- [ ] Offline dot appears (grey) after logout or closing the tab
- [ ] Logout redirects to the login page and blocks access to `/chat`
- [ ] Logging back in restores the full chat history
- [ ] Wrong password shows a clear error, not a crash
- [ ] Empty message is blocked with an error, not sent
- [ ] Registering an already-taken username shows a clear error
- [ ] Mismatched password/confirm-password is blocked at registration

---

## 12. GitHub Deployment (from zero)

1. Create a free account at [github.com](https://github.com) if you don't have one.
2. Click **New repository**, give it a name (e.g. `real-time-communication-app`), and create it **empty** (no README/`.gitignore`, since this project already includes its own).
3. Open the project folder in VS Code (or any editor) and open its terminal.
4. Run the following commands one by one:

```bash
git init
git add .
git commit -m "Initial Real-Time Communication App"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

**What each command does:**
- `git init` — turns the folder into a Git repository.
- `git add .` — stages every file for the first commit.
- `git commit -m "..."` — saves a snapshot of the project with a message.
- `git branch -M main` — names the main branch `main`.
- `git remote add origin ...` — links your local project to the GitHub repository you created (replace `YOUR_GITHUB_REPOSITORY_URL` with the URL GitHub gives you, e.g. `https://github.com/your-username/real-time-communication-app.git`).
- `git push -u origin main` — uploads your code to GitHub.

### GitHub Security — never upload:

- `.env`
- API keys
- Passwords
- `SECRET_KEY` values
- Any database secrets

The included `.gitignore` already excludes `.env` and the SQLite
database file so you don't upload them by accident.

---

## 13. Render Deployment (Free)

1. Push the project to GitHub first (see above).
2. Go to [render.com](https://render.com) and sign up / log in (no credit card required for the free tier).
3. Click **New +** → **Web Service**.
4. Connect your GitHub account and select this repository.
5. Configure the service:
   - **Environment:** Python 3
   - **Build Command:**
     ```
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```
     gunicorn --worker-class gthread --threads 100 --workers 1 --bind 0.0.0.0:$PORT run:app
     ```
6. Add the environment variable:
   - Open the **Environment** section of the service settings.
   - Click **Add Environment Variable**.
   - Key: `SECRET_KEY`
   - Value: a long random string (you can generate one locally with `python -c "import secrets; print(secrets.token_hex(32))"`)
7. Click **Create Web Service**. Render builds and deploys automatically.
8. Once deployed, Render gives you a public URL such as:
   ```
   https://your-app-name.onrender.com
   ```

### What the start command means

| Part | Meaning |
|---|---|
| `gunicorn` | The production web server that runs the app |
| `--worker-class gthread` | Uses a threaded worker, required for Flask-SocketIO's threading mode |
| `--threads 100` | Allows many simultaneous connections in that one worker |
| `--workers 1` | A single worker process — enough for a free-tier student project |
| `--bind 0.0.0.0:$PORT` | Listens on the port Render assigns via the `PORT` environment variable |
| `run:app` | Run the `app` object defined inside `run.py` |

---

## 14. Environment Variables

| Variable      | Required | Description                                    |
|---------------|----------|-------------------------------------------------|
| `SECRET_KEY`  | Yes      | Used by Flask to cryptographically sign session cookies |
| `PORT`        | No       | Set automatically by Render at deploy time      |

See `.env.example` for the format. Never commit a real `.env` file.

## 15. Security

- Passwords are hashed with `werkzeug.security.generate_password_hash` and verified with `check_password_hash` — never stored or compared in plain text.
- User identity is tracked with signed, server-side Flask sessions, not client-editable cookies.
- `SECRET_KEY` is read from an environment variable, never hard-coded.
- No API keys of any kind are used anywhere in the project.
- All SQL queries use parameterized placeholders (`?`), which prevents SQL injection.
- Message text is escaped in the browser before being inserted into the page, reducing the risk of stored/reflected XSS.
- Empty messages, duplicate usernames, and mismatched passwords are all rejected with clear error messages.
- `.gitignore` keeps `.env` and the local SQLite database file out of version control.

## 16. Limitations

- SQLite is a single file; it is not designed for many simultaneous writers at very high scale.
- On Render's free tier, local filesystem storage is not guaranteed to persist forever — a redeploy or service recreation can reset the SQLite file.
- Only one-to-one chat is supported; there is no group chat.
- There is no file, image, voice, or video sharing.
- Presence (online/offline) is tracked in memory on a single server process; it would need adjustment for a multi-server deployment.

## 17. Future Enhancements

- Group chat
- File and image sharing
- Voice / video calling
- Message read receipts
- Message reactions
- Full-text search within conversations
- Switch from SQLite to PostgreSQL for persistent, production-grade storage
- Push notifications
- End-to-end encryption

## 18. Conclusion

This project demonstrates a complete, working real-time chat
application built on a simple, well-understood, and entirely free
technology stack: Flask for the backend, Flask-SocketIO for real-time
communication, SQLite for storage, and plain HTML/CSS/JavaScript for a
professional, responsive frontend — with secure password hashing and
session handling throughout, and clear instructions to run it locally
and deploy it for free on Render.

---

## 19. Simple Concept Explanations

**What is Flask?**
Flask is the Python framework that runs the website and the server. It
decides what happens when someone visits a page like `/login`.
*Simple meaning: Flask is the "engine" of the website.*

**What is Socket.IO?**
Socket.IO keeps an open, continuous connection between the browser and
the server, so the server can push new information (like a new
message) to the browser at any moment.
*Simple meaning: The user does not need to refresh the page to see a new message.*

**What is SQLite?**
SQLite stores the registered users and their chat messages in a single
database file on disk.
*Simple meaning: It's the "notebook" where the app permanently writes down every user and every message.*

**What is a session?**
A session lets the server remember which user is logged in, across
different pages and requests, without asking them to log in again on
every click.
*Simple meaning: It's how the server "remembers you" after you log in.*

**What is a user_id?**
Each registered user gets a unique number assigned automatically by the
database. The app uses this number — not the username or a phone
number — to know exactly who is sending and who is receiving a
message.
*Simple meaning: It's like an ID card number for each user inside the app.*

**What is a Socket.IO room?**
A "room" is a private channel that only specific connections belong
to. Every user automatically joins a room named after their own
`user_id` (e.g. `user_101`), so the server can send a message to
exactly the right person.
*Simple meaning: It's a private mailbox that belongs to one user.*

## 20. Real-Time Message Flow

```
Kavi opens the chat page
        |
        v
Kavi types "Hello Priya"
        |
        v
JavaScript (script.js) reads the message
        |
        v
Socket.IO sends a "send_message" event to the server
        |
        v
Flask-SocketIO receives the event
        |
        v
The server identifies the receiver (Priya's user_id)
        |
        v
The message is saved into the SQLite "messages" table
        |
        v
The server sends the message into Priya's private room ("user_102")
        |
        v
Priya's browser receives the "receive_message" event
        |
        v
The message appears on Priya's screen immediately, with no refresh
```

**Simple meaning of each step:** Kavi's message travels from his
browser, to the server, gets saved so it's never lost, and is pushed
straight to Priya's screen — all in a fraction of a second, without
Priya ever having to press refresh.

---

## 21. Common Errors and Solutions

| Error | Likely Cause | Solution |
|---|---|---|
| `ModuleNotFoundError` | Dependencies not installed / venv not activated | Run `pip install -r requirements.txt` inside your activated virtual environment |
| Application failed to start (on Render) | Wrong Start Command | Check that the Start Command is exactly the Gunicorn command shown above |
| Port error | App is not binding to the port Render provides | Make sure the app uses `0.0.0.0:$PORT` (already handled in this project) |
| `SECRET_KEY` missing / sessions not working | Environment variable not set | Add `SECRET_KEY` under Render's Environment Variables section |
| Socket.IO not working / messages don't arrive instantly | Wrong Gunicorn worker settings, or testing in the same browser tab twice | Use the exact Start Command above, and test with two separate browser sessions |
| 404 on a page | Wrong URL, or route/template name mismatch | Check the Flask routes in `app/routes.py` and the deployed URL |
| "Invalid username or password" unexpectedly | Username is case-sensitive, extra spaces, or wrong account | Double-check the exact username used at registration |
| Data disappears after redeploying on Render | Free tier storage isn't guaranteed to persist | Expected on the free tier — see the Database Deployment Note above; move to PostgreSQL for permanent storage |

---

## 22. Internship Presentation Content

**PROJECT TITLE:** Real-Time Communication App

**PROBLEM STATEMENT:** See Section 2 above.

**OBJECTIVES:** See Section 3 above.

**PROPOSED SYSTEM:** A web-based, username/password-authenticated chat
application that delivers messages instantly using Socket.IO, backed by
a SQLite database, deployable for free on Render.

**MODULES:**
1. Authentication Module
2. User Management Module
3. Real-Time Messaging Module
4. Presence Module
5. Chat History Module
6. Database Module

**SYSTEM ARCHITECTURE:** See Section 6 above.

**DATABASE DESIGN:** See Section 8 above.

**SOFTWARE REQUIREMENTS:**
- Python 3.10+
- Flask, Flask-SocketIO, Werkzeug, Gunicorn (see `requirements.txt`)
- A modern web browser
- Git, GitHub account, Render account

**HARDWARE REQUIREMENTS:**
- Any computer capable of running Python 3 (for local development)
- Internet connection (for deployment and multi-device testing)

**ADVANTAGES:**
- No phone number, OTP, or paid API required
- Free to build and free to deploy
- Real-time delivery with no page refresh
- Simple, readable, well-documented codebase suitable for a student project

**LIMITATIONS:** See Section 16 above.

**FUTURE ENHANCEMENTS:** See Section 17 above.

**CONCLUSION:** See Section 18 above.

---

## 23. Viva Questions and Answers

1. **What is Flask?**
   Flask is a lightweight Python web framework used to build the
   backend of this application — it handles routes, sessions, and
   rendering pages.

2. **What is Socket.IO?**
   Socket.IO is a library that keeps a persistent, two-way connection
   open between the browser and the server, allowing instant,
   event-based communication instead of normal request/response.

3. **Why did you use Flask-SocketIO?**
   It integrates Socket.IO directly with Flask, so the same application
   can serve normal web pages and handle real-time chat events together.

4. **Why don't you use phone numbers?**
   The project's requirement was authentication without a phone number
   or OTP service, so usernames and passwords are used instead — this
   also avoids any dependency on a paid SMS provider.

5. **What is SQLite?**
   SQLite is a lightweight, file-based relational database that
   requires no separate server process, making it ideal for a student
   project.

6. **How does real-time communication work in this project?**
   The browser and server keep an open Socket.IO connection. When a
   user sends a message, the server receives it as an event, saves it
   to the database, and immediately emits it to the receiver's private
   room.

7. **How is a user identified?**
   Every user gets a unique, auto-incrementing `user_id` from the
   database when they register; this ID (not the username) is used
   internally to route messages.

8. **How are passwords stored?**
   Passwords are hashed using Werkzeug's `generate_password_hash`
   before being saved, and verified with `check_password_hash` — the
   plain-text password is never stored.

9. **What is a session?**
   A session is server-side state, identified by a signed cookie, that
   lets the server remember which user is logged in across different
   requests.

10. **What is a Socket.IO room?**
    A room is a named group that specific socket connections join; this
    project gives every user their own private room (`user_<id>`) so
    messages can be routed to exactly the right person.

11. **How is chat history stored?**
    Every message is inserted into the `messages` table in SQLite with
    the sender's ID, receiver's ID, message text, and timestamp; it is
    reloaded whenever that conversation is opened again.

12. **What happens when a user disconnects?**
    The server's `disconnect` Socket.IO event handler removes that user
    from the in-memory online-users list and broadcasts the updated
    list, so other users see them go offline.

13. **Why is Gunicorn used?**
    Flask's built-in development server is not meant for production;
    Gunicorn is a production-grade WSGI server used to actually serve
    the app once it's deployed.

14. **Why is Render used?**
    Render offers a free Web Service tier that can build and run a
    Flask application directly from a GitHub repository, with no credit
    card required.

15. **What is GitHub used for here?**
    GitHub hosts the project's source code and connects directly to
    Render, so pushing new code can automatically trigger a new
    deployment.

16. **What is the difference between normal HTTP and WebSocket (Socket.IO) communication?**
    HTTP is request/response — the browser must ask for new data. A
    WebSocket-based connection like Socket.IO stays open, so the server
    can push new data to the browser at any time without being asked.

17. **How does the typing indicator work?**
    While a user types, the browser emits a `typing` Socket.IO event to
    the server, which forwards it to the other user's room; a
    `stop_typing` event (or a short timeout) clears the indicator.

18. **How is a duplicate username handled?**
    At registration, the server checks the `users` table for an
    existing row with the same username before inserting a new one, and
    shows a clear error if it already exists.

19. **How is an empty message prevented from being sent?**
    Both the JavaScript client and the server-side Socket.IO handler
    check that the trimmed message is not empty before saving or
    broadcasting it.

20. **What would you change to make this production-ready?**
    Replace SQLite with a persistent hosted database like PostgreSQL,
    add rate limiting and input length limits, and consider running
    multiple worker processes behind a message broker for very large
    scale.
