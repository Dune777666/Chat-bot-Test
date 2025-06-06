window.onload = () => {
  addBotMessage("Hi there! 👋 I’m MONICA. How can I assist you today?");
  addMenuButton();
};

function addMenuButton() {
  const chat = document.getElementById("chat-window");
  const menuBtn = document.createElement("button");
  menuBtn.className = "menu-button";
  menuBtn.textContent = "Menu";
  menuBtn.onclick = showMenuList;
  chat.appendChild(menuBtn);
  chat.scrollTop = chat.scrollHeight;
}

function showMenuList() {
  const chat = document.getElementById("chat-window");
  // Remove any existing menu list
  const oldMenu = document.getElementById("menu-list");
  if (oldMenu) oldMenu.remove();
  const menuDiv = document.createElement("div");
  menuDiv.id = "menu-list";
  menuDiv.className = "menu-list";
  const menuItems = [
    "Check VPN connectivity for remote users.",
    "Trace route to payments gateway server.",
    "Trigger a health check on branch systems in Region West.",
    "Raise a P1 ticket for network outage in Mumbai branch.",
    "Show all open tickets assigned to the Infra Team.",
    "Temporarily disable access to user john.k@bank.com",
    "Deploy patch KB5025341 to all Windows 10 VMs.",
    "How do I reset my AD password?",
    "My system is very slow. What can I do?",
    "Is there any current outage reported in the Data Center?",
    "What’s the status of Core Banking Server CBX-01?",
    "Who last accessed the SWIFT server?",
    "Is there a scheduled maintenance this weekend?",
    "Who is on call for security today?",
    "When was the last DR drill performed?"
  ];
  menuItems.forEach(q => {
    const btn = document.createElement("button");
    btn.className = "menu-button";
    btn.textContent = q;
    btn.onclick = () => sendMenuQuestion(q);
    menuDiv.appendChild(btn);
  });
  chat.appendChild(menuDiv);
  chat.scrollTop = chat.scrollHeight;
}

function sendMenuQuestion(q) {
  addUserMessage(q);
  // Remove menu after selection
  const oldMenu = document.getElementById("menu-list");
  if (oldMenu) oldMenu.remove();
  fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: q })
  })
    .then(res => res.json())
    .then(data => addBotMessage(data.response))
    .catch(() => addBotMessage('Sorry, there was an error.'));
}

function sendMessage() {
  const input = document.getElementById("userInput");
  const message = input.value.trim();
  if (message) {
    addUserMessage(message);
    input.value = "";
    setTimeout(() => addBotMessage("Let me process that..."), 500);
    // The backend will auto-detect language
    fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => addBotMessage(data.response))
    .catch(() => addBotMessage('Sorry, there was an error.'));
  }
}

function addUserMessage(text) {
  const chat = document.getElementById("chat-window");
  const bubble = document.createElement("div");
  bubble.className = "chat-bubble user";
  bubble.textContent = text;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;
}

function addBotMessage(text, withMenu = false) {
  const chat = document.getElementById("chat-window");
  const bubble = document.createElement("div");
  bubble.className = "chat-bubble bot";

  // Add bot image to every bot message
  const botImg = document.createElement("img");
  botImg.src = "/static/bot.png";
  botImg.alt = "Bot";
  botImg.className = "bot-avatar bot-inline";
  bubble.appendChild(botImg);

  const msgSpan = document.createElement("span");
  msgSpan.textContent = text;
  bubble.appendChild(msgSpan);

  chat.appendChild(bubble);
  if (withMenu) {
    const menuBtn = document.createElement("button");
    menuBtn.className = "menu-button";
    menuBtn.textContent = "Menu";
    menuBtn.style.display = "block";
    menuBtn.style.margin = "10px 0 0 0";
    menuBtn.onclick = showMenuOptions;
    chat.appendChild(menuBtn);
  }
  chat.scrollTop = chat.scrollHeight;
}
