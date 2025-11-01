// Matrix background effect
function createMatrixEffect() {
    const canvas = document.createElement('canvas');
    const container = document.getElementById('matrix');
    container.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';
    const fontSize = 14;
    let columns = Math.floor(canvas.width / fontSize);
    let drops = Array(columns).fill(1);

    function draw() {
        ctx.fillStyle = 'rgba(5, 8, 20, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#00ff41';
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
            const text = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    setInterval(draw, 33);

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        // Recalculate columns and drops array
        columns = Math.floor(canvas.width / fontSize);
        drops = Array(columns).fill(1);
    });
}

// Initialize
let queryCount = 0;
let startTime = Date.now();

// Update uptime
function updateUptime() {
    const elapsed = Date.now() - startTime;
    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    
    document.getElementById('uptime').textContent = 
        `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

setInterval(updateUptime, 1000);

// Chat functionality
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

function addMessage(type, text, model = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    let prompt = '';
    if (type === 'user') prompt = 'USER:';
    else if (type === 'ai') prompt = model ? `MAMAR.AI [${model.toUpperCase()}]:` : 'MAMAR.AI:';
    else if (type === 'system') prompt = 'SYSTEM:';
    
    // Create elements safely to prevent XSS
    const promptSpan = document.createElement('span');
    promptSpan.className = 'prompt';
    promptSpan.textContent = prompt;
    
    const textSpan = document.createElement('span');
    textSpan.className = 'text';
    textSpan.textContent = text;
    
    messageDiv.appendChild(promptSpan);
    messageDiv.appendChild(textSpan);
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai typing';
    typingDiv.id = 'typing';
    typingDiv.innerHTML = `
        <span class="prompt">MAMAR.AI:</span>
        <span class="text">Processing</span>
    `;
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideTyping() {
    const typingDiv = document.getElementById('typing');
    if (typingDiv) {
        typingDiv.remove();
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Get selected model
    const selectedModel = document.querySelector('input[name="model"]:checked').value;
    const model = selectedModel === 'auto' ? null : selectedModel;

    // Add user message
    addMessage('user', message);
    messageInput.value = '';

    // Show typing indicator
    showTyping();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message, model })
        });

        const data = await response.json();

        hideTyping();

        if (data.success) {
            addMessage('ai', data.response, data.model);
            queryCount++;
            document.getElementById('queryCount').textContent = queryCount;
        } else {
            addMessage('system', `Error: ${data.error}`);
        }
    } catch (error) {
        hideTyping();
        addMessage('system', `Connection error: ${error.message}`);
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Quick commands
document.querySelectorAll('.quick-cmd').forEach(btn => {
    btn.addEventListener('click', () => {
        messageInput.value = btn.dataset.cmd;
        sendMessage();
    });
});

// Check system status
async function checkStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        if (data.status === 'online') {
            document.getElementById('status').style.color = '#00ff41';
            document.getElementById('systemStatus').textContent = 'ACTIVE';
        }
    } catch (error) {
        document.getElementById('status').style.color = '#ff0000';
        document.getElementById('systemStatus').textContent = 'ERROR';
    }
}

// Initialize
createMatrixEffect();
checkStatus();
setInterval(checkStatus, 30000); // Check every 30 seconds

// Focus input on load
messageInput.focus();
