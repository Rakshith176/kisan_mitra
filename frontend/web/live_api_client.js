class LiveAPIClient {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.sessionId = Date.now().toString();
        
        this.connect();
        this.setupEventListeners();
    }
    
    connect() {
        const wsUrl = `ws://localhost:8000/live/ws/${this.sessionId}`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateStatus('Connected to Live API', true);
            console.log('Connected to Live API');
        };
        
        this.ws.onmessage = (event) => {
            this.handleResponse(JSON.parse(event.data));
        };
        
        this.ws.onclose = () => {
            this.isConnected = false;
            this.updateStatus('Disconnected from Live API', false);
            console.log('Disconnected from Live API');
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('Connection Error', false);
        };
    }
    
    setupEventListeners() {
        // Handle Enter key in message input
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    this.sendTextMessage();
                }
            });
        }
    }
    
    handleResponse(data) {
        const messagesDiv = document.getElementById('messages');
        
        switch (data.type) {
            case 'live_response':
                const chunk = data.chunk;
                if (chunk.text) {
                    this.addMessage(chunk.text, false);
                }
                if (chunk.audio) {
                    this.playAudio(chunk.audio);
                }
                break;
                
            case 'tool_result':
                this.addMessage(`Tool ${data.tool_name}: ${data.result}`, false);
                break;
                
            case 'error':
                this.addMessage(`Error: ${data.message}`, false);
                break;
        }
    }
    
    addMessage(text, isUser) {
        const messagesDiv = document.getElementById('messages');
        
        // Remove empty state if it exists
        const emptyState = messagesDiv.querySelector('.empty-state');
        if (emptyState) {
            emptyState.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
        
        const messageText = document.createElement('div');
        messageText.textContent = text;
        messageDiv.appendChild(messageText);
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        messageDiv.appendChild(timeDiv);
        
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    sendTextMessage() {
        const input = document.getElementById('messageInput');
        const text = input.value.trim();
        
        if (text && this.isConnected) {
            this.addMessage(text, true);
            this.ws.send(JSON.stringify({
                type: 'text',
                content: text,
                language: 'en'
            }));
            input.value = '';
        } else if (!this.isConnected) {
            this.addMessage('Not connected to Live API. Please wait...', false);
        }
    }
    
    async toggleRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            await this.stopRecording();
        }
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                this.processAudio();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Update UI
            const recordBtn = document.getElementById('recordBtn');
            recordBtn.textContent = '⏹️ Stop Recording';
            recordBtn.className = 'btn btn-danger';
            
            const recordingIndicator = document.getElementById('recordingIndicator');
            recordingIndicator.classList.add('show');
            
        } catch (error) {
            console.error('Recording failed:', error);
            this.addMessage(`Recording failed: ${error.message}`, false);
        }
    }
    
    async stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Update UI
            const recordBtn = document.getElementById('recordBtn');
            recordBtn.textContent = '🎤 Start Recording';
            recordBtn.className = 'btn btn-secondary';
            
            const recordingIndicator = document.getElementById('recordingIndicator');
            recordingIndicator.classList.remove('show');
        }
    }
    
    async processAudio() {
        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            
            reader.onload = () => {
                const base64Audio = reader.result.split(',')[1];
                this.ws.send(JSON.stringify({
                    type: 'audio',
                    content: base64Audio,
                    language: 'en'
                }));
                
                this.addMessage('🎤 Audio message sent', true);
            };
            
            reader.readAsDataURL(audioBlob);
            
        } catch (error) {
            console.error('Audio processing failed:', error);
            this.addMessage(`Audio processing failed: ${error.message}`, false);
        }
    }
    
    requestTool(toolName, parameters) {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'tool_request',
                tool_name: toolName,
                parameters: parameters
            }));
            
            this.addMessage(`🔧 Requesting ${toolName}...`, true);
        } else {
            this.addMessage('Not connected to Live API. Please wait...', false);
        }
    }
    
    playAudio(base64Audio) {
        try {
            const audio = new Audio(`data:audio/wav;base64,${base64Audio}`);
            audio.play().catch(error => {
                console.error('Audio playback failed:', error);
                this.addMessage('Audio response received but playback failed', false);
            });
        } catch (error) {
            console.error('Audio creation failed:', error);
        }
    }
    
    updateStatus(message, connected) {
        const statusDiv = document.getElementById('status');
        const statusIcon = document.getElementById('statusIcon');
        const statusText = document.getElementById('statusText');
        
        if (statusDiv && statusIcon && statusText) {
            statusText.textContent = message;
            statusDiv.className = `status ${connected ? 'connected' : 'disconnected'}`;
            statusIcon.textContent = connected ? '✅' : '❌';
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
        }
    }
}

// Initialize client when page loads
let client;

document.addEventListener('DOMContentLoaded', () => {
    client = new LiveAPIClient();
});

// Global functions for HTML buttons
function sendTextMessage() {
    if (client) {
        client.sendTextMessage();
    }
}

function toggleRecording() {
    if (client) {
        client.toggleRecording();
    }
}

function requestTool(toolName, parameters) {
    if (client) {
        client.requestTool(toolName, parameters);
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendTextMessage();
    }
}

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (client) {
        client.disconnect();
    }
});

// Reconnection logic
function reconnect() {
    if (client) {
        client.disconnect();
        setTimeout(() => {
            client = new LiveAPIClient();
        }, 1000);
    }
}

// Add reconnection button to status bar
document.addEventListener('DOMContentLoaded', () => {
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        const reconnectBtn = document.createElement('button');
        reconnectBtn.textContent = '🔄 Reconnect';
        reconnectBtn.className = 'btn btn-secondary';
        reconnectBtn.style.marginLeft = '16px';
        reconnectBtn.style.padding = '4px 8px';
        reconnectBtn.style.fontSize = '12px';
        reconnectBtn.onclick = reconnect;
        
        statusDiv.appendChild(reconnectBtn);
    }
});
