// Chat widget connecté au backend
let chatOpen = false;

function toggleChat() {
    chatOpen = !chatOpen;
    document.getElementById('chat-bubble').style.display = chatOpen ? 'none' : 'block';
    document.getElementById('chat-box').style.display = chatOpen ? 'block' : 'none';
    if (chatOpen) loadChatMessages();
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';
    await fetch('/api/chat/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: msg })
    });
    loadChatMessages();
}

async function loadChatMessages() {
    const chatBody = document.getElementById('chat-body');
    chatBody.innerHTML = '<div style="color:#888;text-align:center;">Chargement...</div>';
    try {
        const res = await fetch('/api/chat/messages');
        const messages = await res.json();
        chatBody.innerHTML = '';
        messages.forEach(m => {
            const div = document.createElement('div');
            div.className = 'chat-message ' + (m.sender === 'client' ? 'user' : 'support');
            div.textContent = (m.sender === 'client' ? 'Moi: ' : 'Support: ') + m.message;
            chatBody.appendChild(div);
        });
        chatBody.scrollTop = chatBody.scrollHeight;
    } catch (e) {
        chatBody.innerHTML = '<div style="color:#c00;text-align:center;">Erreur de chargement du chat</div>';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('chat-input');
    if (input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    }
    // Rafraîchissement auto si la bulle est ouverte
    setInterval(() => { if (chatOpen) loadChatMessages(); }, 3000);
});
