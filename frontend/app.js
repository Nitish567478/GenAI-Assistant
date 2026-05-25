document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.getElementById('new-chat');
    const historyList = document.getElementById('history-list');
    const loading = document.getElementById('loading');
    const emojiTrigger = document.getElementById('emoji-trigger');

    let sessions = {};
    let currentSessionId = '';

    // Initialization logic
    function init() {
        try {
            const stored = localStorage.getItem('chatSessions');
            sessions = stored ? JSON.parse(stored) : {};
        } catch (e) {
            sessions = {};
        }

        currentSessionId = localStorage.getItem('currentSessionId');

        // Safety: Ensure sessions is an object and currentSession exists
        if (typeof sessions !== 'object' || sessions === null) sessions = {};
        
        if (!currentSessionId || !sessions[currentSessionId]) {
            currentSessionId = createNewSession();
        }

        renderHistory();
        renderMessages();
    }

    function createNewSession() {
        const id = 'session_' + Date.now();
        sessions[id] = {
            id: id,
            title: 'New Chat',
            messages: []
        };
        save();
        return id;
    }

    function save() {
        localStorage.setItem('chatSessions', JSON.stringify(sessions));
        localStorage.setItem('currentSessionId', currentSessionId);
    }

    function renderHistory() {
        if (!historyList) return;
        historyList.innerHTML = '';
        
        const sortedSessions = Object.values(sessions).sort((a, b) => {
            const timeA = parseInt(a.id.split('_')[1]);
            const timeB = parseInt(b.id.split('_')[1]);
            return timeB - timeA;
        });

        sortedSessions.forEach(session => {
            const item = document.createElement('div');
            item.className = `history-item ${session.id === currentSessionId ? 'active' : ''}`;
            item.innerHTML = `
                <span class="history-text">${session.title || 'New Chat'}</span>
                <div class="menu-trigger">⋮</div>
                <div class="popover">
                    <div class="delete-btn">Delete</div>
                </div>
            `;
            
            item.onclick = (e) => {
                if (!e.target.classList.contains('delete-btn') && !e.target.classList.contains('menu-trigger')) {
                    switchSession(session.id);
                }
            };

            const trigger = item.querySelector('.menu-trigger');
            const popover = item.querySelector('.popover');
            const deleteBtn = item.querySelector('.delete-btn');

            trigger.onclick = (e) => {
                e.stopPropagation();
                document.querySelectorAll('.popover').forEach(p => p !== popover && p.classList.remove('show'));
                popover.classList.toggle('show');
            };

            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                deleteSession(session.id);
            };

            historyList.appendChild(item);
        });
    }

    function switchSession(id) {
        currentSessionId = id;
        save();
        renderHistory();
        renderMessages();
    }

    function deleteSession(id) {
        delete sessions[id];
        const sessionKeys = Object.keys(sessions);
        if (currentSessionId === id) {
            currentSessionId = sessionKeys.length > 0 ? sessionKeys[sessionKeys.length - 1] : createNewSession();
        }
        save();
        renderHistory();
        renderMessages();
    }

    function renderMessages() {
        if (!chatContainer) return;
        chatContainer.innerHTML = '';
        const session = sessions[currentSessionId];
        
        if (!session || !session.messages || session.messages.length === 0) {
            appendFullMessage('assistant', "How can I help you today?", null);
        } else {
            session.messages.forEach(msg => {
                appendFullMessage(msg.role, msg.content, msg.metadata);
            });
        }
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function appendFullMessage(role, content, metadata) {
        const row = document.createElement('div');
        row.className = `message-row ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.innerHTML = role === 'user' ? '👤' : '🤖';

        const textContent = document.createElement('div');
        textContent.className = 'content';
        textContent.innerText = content;

        if (metadata) {
            const meta = document.createElement('div');
            meta.className = 'metadata';
            meta.innerText = `Tokens: ${metadata.tokensUsed} | Chunks: ${metadata.retrievedChunks}`;
            textContent.appendChild(meta);
        }

        row.appendChild(avatar);
        row.appendChild(textContent);
        chatContainer.appendChild(row);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Show user message
        appendFullMessage('user', message, null);
        
        // Save to current session
        const session = sessions[currentSessionId];
        if (session.messages.length === 0) {
            session.title = message.substring(0, 25) + (message.length > 25 ? '...' : '');
            renderHistory();
        }
        session.messages.push({ role: 'user', content: message, metadata: null });
        save();

        userInput.value = '';
        loading.classList.remove('hidden');
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sessionId: currentSessionId, message })
            });

            const data = await response.json();
            loading.classList.add('hidden');

            if (response.ok) {
                const metadata = { tokensUsed: data.tokensUsed, retrievedChunks: data.retrievedChunks };
                appendFullMessage('assistant', data.reply, metadata);
                session.messages.push({ role: 'assistant', content: data.reply, metadata });
                save();
            } else {
                const errMsg = data.detail || 'Server error';
                appendFullMessage('assistant', `Error: ${errMsg}`, null);
            }
        } catch (error) {
            loading.classList.add('hidden');
            appendFullMessage('assistant', 'Error: Connection failed.', null);
        }
    }

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    newChatBtn.addEventListener('click', () => {
        currentSessionId = createNewSession();
        switchSession(currentSessionId);
    });

    // Emoji Picker
    const emojis = ['😊', '😂', '🔥', '👍', '🙏', '💡', '🚀', '🤔', '✅', '❌'];
    emojiTrigger.addEventListener('click', (e) => {
        const existingPicker = document.querySelector('.emoji-picker');
        if (existingPicker) {
            existingPicker.remove();
            return;
        }

        const picker = document.createElement('div');
        picker.className = 'emoji-picker';
        picker.style.cssText = `
            position: absolute; bottom: 80px; left: 15%; 
            background: #202123; border: 1px solid #4d4d4d;
            padding: 10px; border-radius: 8px; display: grid;
            grid-template-columns: repeat(5, 1fr); gap: 5px; z-index: 1000;
        `;
        emojis.forEach(emoji => {
            const btn = document.createElement('span');
            btn.innerText = emoji;
            btn.style.cursor = 'pointer';
            btn.onclick = () => {
                userInput.value += emoji;
                picker.remove();
            };
            picker.appendChild(btn);
        });
        document.body.appendChild(picker);
        e.stopPropagation();
        document.addEventListener('click', () => picker.remove(), { once: true });
    });

    // Global click to hide popovers
    document.addEventListener('click', () => {
        document.querySelectorAll('.popover').forEach(p => p.classList.remove('show'));
    });

    init();
});
