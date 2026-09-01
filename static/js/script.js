// ---------------------------------------------------------------------
// script.js - connects the browser to the Flask-SocketIO server and
// runs the whole chat UI: user list, chat history, sending/receiving
// messages, typing indicator, and online/offline status.
// ---------------------------------------------------------------------

(function () {
  const appEl = document.getElementById("chat-app");
  const myUserId = parseInt(appEl.dataset.userId, 10);
  const myUsername = appEl.dataset.username;

  const userListEl = document.getElementById("user-list");
  const userSearchEl = document.getElementById("user-search");
  const chatMessagesEl = document.getElementById("chat-messages");
  const chatHeaderName = document.getElementById("chat-header-name");
  const chatHeaderStatus = document.getElementById("chat-header-status");
  const typingIndicatorEl = document.getElementById("typing-indicator");
  const messageInput = document.getElementById("message-input");
  const sendBtn = document.getElementById("send-btn");
  const chatForm = document.getElementById("chat-input-form");
  const chatErrorEl = document.getElementById("chat-error");

  let users = [];              // [{id, username}] - full list from the server
  let onlineUserIds = new Set();
  let selectedUserId = null;
  let searchTerm = "";
  let typingTimeout = null;
  let stopTypingTimer = null;

  // ---- Helpers -------------------------------------------------------

  function escapeHtml(str) {
    // Basic escaping to reduce XSS risk when inserting message text.
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  function formatTime(isoString) {
    if (!isoString) return "";
    // SQLite CURRENT_TIMESTAMP is UTC "YYYY-MM-DD HH:MM:SS"; make it
    // parseable by the Date constructor.
    const normalized = isoString.replace(" ", "T") + "Z";
    const d = new Date(normalized);
    if (isNaN(d.getTime())) return "";
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function showChatError(msg) {
    chatErrorEl.textContent = msg;
    setTimeout(() => {
      if (chatErrorEl.textContent === msg) chatErrorEl.textContent = "";
    }, 4000);
  }

  // ---- Rendering -------------------------------------------------------

  function renderUserList() {
    userListEl.innerHTML = "";

    // Apply the search filter (case-insensitive substring match on username)
    // so users can quickly find someone in a long contact list.
    const visibleUsers = searchTerm
      ? users.filter((u) => u.username.toLowerCase().includes(searchTerm))
      : users;

    if (visibleUsers.length === 0) {
      const empty = document.createElement("li");
      empty.className = "user-item-empty";
      empty.textContent = users.length === 0 ? "No other users yet." : "No users match your search.";
      userListEl.appendChild(empty);
      return;
    }

    visibleUsers.forEach((user) => {
      const li = document.createElement("li");
      li.className = "user-item" + (user.id === selectedUserId ? " active" : "");
      li.dataset.userId = user.id;

      const dot = document.createElement("span");
      dot.className = "status-dot " + (onlineUserIds.has(user.id) ? "online" : "");

      const name = document.createElement("span");
      name.textContent = user.username;

      li.appendChild(dot);
      li.appendChild(name);
      li.addEventListener("click", () => selectUser(user.id));
      userListEl.appendChild(li);
    });
  }

  function renderChatHeader() {
    const user = users.find((u) => u.id === selectedUserId);
    if (!user) {
      chatHeaderName.textContent = "Select a user to start chatting";
      chatHeaderStatus.textContent = "";
      return;
    }
    chatHeaderName.textContent = user.username;
    chatHeaderStatus.textContent = onlineUserIds.has(user.id) ? "Online" : "Offline";
  }

  function renderMessages(messages) {
    chatMessagesEl.innerHTML = "";
    if (messages.length === 0) {
      const placeholder = document.createElement("div");
      placeholder.className = "chat-placeholder";
      placeholder.textContent = "No messages yet. Say hello!";
      chatMessagesEl.appendChild(placeholder);
      return;
    }
    messages.forEach(appendMessage);
    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
  }

  function appendMessage(msg) {
    // Remove "no messages yet" / "select a user" placeholders if present.
    const placeholder = chatMessagesEl.querySelector(".chat-placeholder");
    if (placeholder) placeholder.remove();

    const isMe = msg.sender_id === myUserId;
    const row = document.createElement("div");
    row.className = "message-row " + (isMe ? "me" : "them");

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = escapeHtml(msg.message) + '<span class="bubble-time">' + formatTime(msg.created_at) + "</span>";

    row.appendChild(bubble);
    chatMessagesEl.appendChild(row);
    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
  }

  // ---- Data loading ----------------------------------------------------

  function loadUsers() {
    fetch("/users")
      .then((res) => res.json())
      .then((data) => {
        users = data;
        renderUserList();
        renderChatHeader();
      })
      .catch(() => showChatError("Could not load the user list."));
  }

  function loadHistory(otherUserId) {
    fetch("/messages/" + otherUserId)
      .then((res) => res.json())
      .then((data) => renderMessages(data))
      .catch(() => showChatError("Could not load chat history."));
  }

  function selectUser(userId) {
    selectedUserId = userId;
    messageInput.disabled = false;
    sendBtn.disabled = false;
    typingIndicatorEl.textContent = "";
    renderUserList();
    renderChatHeader();
    loadHistory(userId);
    messageInput.focus();
  }

  // ---- Socket.IO ---------------------------------------------------------

  const socket = io();

  socket.on("connect", () => {
    // Connected. Server will broadcast the online_users list shortly.
  });

  socket.on("online_users", (ids) => {
    onlineUserIds = new Set(ids);
    renderUserList();
    renderChatHeader();
  });

  socket.on("receive_message", (msg) => {
    const isRelevant =
      (msg.sender_id === myUserId && msg.receiver_id === selectedUserId) ||
      (msg.sender_id === selectedUserId && msg.receiver_id === myUserId);

    if (isRelevant) {
      appendMessage(msg);
    }
  });

  socket.on("message_error", (data) => {
    showChatError(data.error || "Something went wrong sending that message.");
  });

  socket.on("typing", (data) => {
    if (data.sender_id === selectedUserId) {
      typingIndicatorEl.textContent = data.username + " is typing...";
      clearTimeout(typingTimeout);
      typingTimeout = setTimeout(() => {
        typingIndicatorEl.textContent = "";
      }, 3000);
    }
  });

  socket.on("stop_typing", (data) => {
    if (data.sender_id === selectedUserId) {
      typingIndicatorEl.textContent = "";
    }
  });

  // ---- Sending messages / typing events -----------------------------------

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();

    if (!selectedUserId) {
      showChatError("Select a user first.");
      return;
    }
    if (!message) {
      showChatError("Message cannot be empty.");
      return;
    }

    socket.emit("send_message", { receiver_id: selectedUserId, message: message });
    socket.emit("stop_typing", { receiver_id: selectedUserId });
    messageInput.value = "";
  });

  messageInput.addEventListener("input", () => {
    if (!selectedUserId) return;

    socket.emit("typing", { receiver_id: selectedUserId });

    clearTimeout(stopTypingTimer);
    stopTypingTimer = setTimeout(() => {
      socket.emit("stop_typing", { receiver_id: selectedUserId });
    }, 1500);
  });

  // ---- Search -------------------------------------------------------------

  userSearchEl.addEventListener("input", () => {
    searchTerm = userSearchEl.value.trim().toLowerCase();
    renderUserList();
  });

  // ---- Init -------------------------------------------------------------

  loadUsers();
  // Refresh the user list periodically so newly registered users show up.
  setInterval(loadUsers, 10000);
})();
