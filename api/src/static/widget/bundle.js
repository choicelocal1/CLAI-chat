// CLAI Chat Widget Bundle
// This is a placeholder for the actual widget bundle that would be built using webpack

// Widget namespace
window.CLAIChat = window.CLAIChat || {};

// Widget implementation
window.CLAIChat.Widget = {
    // Widget state
    state: {
        isOpen: false,
        messages: [],
        config: null,
        conversationId: null,
        typing: false
    },
    
    // Initialize the widget
    init: function(config) {
        this.state.config = config;
        this.render();
        this.setupEventListeners();
        this.connectWebSocket();
    },
    
    // Render the widget
    render: function() {
        var container = document.getElementById(this.state.config.containerId);
        if (!container) return;
        
        // Create widget HTML
        var html = `
            <div id="clai-chat-widget">
                <div class="clai-chat-launcher">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z" fill="white"/>
                    </svg>
                </div>
                <div class="clai-chat-window">
                    <div class="clai-chat-header">
                        <div>Chat with ${this.state.config.name}</div>
                        <div class="clai-chat-close">×</div>
                    </div>
                    <div class="clai-chat-messages"></div>
                    <div class="clai-chat-input-area">
                        <input type="text" class="clai-chat-input" placeholder="Type a message...">
                        <button class="clai-chat-send">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="white"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
        // Add welcome message
        this.addMessage("Welcome! How can I help you today?", "bot");
    },
    
    // Setup event listeners
    setupEventListeners: function() {
        var self = this;
        var launcher = document.querySelector('.clai-chat-launcher');
        var closeBtn = document.querySelector('.clai-chat-close');
        var sendBtn = document.querySelector('.clai-chat-send');
        var input = document.querySelector('.clai-chat-input');
        
        // Toggle chat window
        launcher.addEventListener('click', function() {
            self.toggleChat();
        });
        
        closeBtn.addEventListener('click', function() {
            self.toggleChat();
        });
        
        // Send message
        sendBtn.addEventListener('click', function() {
            self.sendMessage();
        });
        
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                self.sendMessage();
            }
        });
    },
    
    // Toggle chat window
    toggleChat: function() {
        var chatWindow = document.querySelector('.clai-chat-window');
        this.state.isOpen = !this.state.isOpen;
        
        if (this.state.isOpen) {
            chatWindow.classList.add('active');
        } else {
            chatWindow.classList.remove('active');
        }
    },
    
    // Send message
    sendMessage: function() {
        var input = document.querySelector('.clai-chat-input');
        var message = input.value.trim();
        
        if (!message) return;
        
        // Add message to UI
        this.addMessage(message, 'human');
        
        // Clear input
        input.value = '';
        
        // Start new conversation if needed
        if (!this.state.conversationId) {
            this.startConversation(message);
        } else {
            this.sendMessageToServer(message);
        }
    },
    
    // Add message to UI
    addMessage: function(content, sender) {
        var messagesContainer = document.querySelector('.clai-chat-messages');
        var messageElement = document.createElement('div');
        messageElement.className = 'clai-chat-message ' + sender;
        messageElement.textContent = content;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Add to messages array
        this.state.messages.push({
            content: content,
            sender: sender,
            timestamp: new Date()
        });
    },
    
    // Show typing indicator
    showTyping: function() {
        if (this.state.typing) return;
        
        this.state.typing = true;
        var messagesContainer = document.querySelector('.clai-chat-messages');
        var typingElement = document.createElement('div');
        typingElement.className = 'clai-chat-typing';
        typingElement.innerHTML = `
            <div class="clai-chat-typing-bubble"></div>
            <div class="clai-chat-typing-bubble"></div>
            <div class="clai-chat-typing-bubble"></div>
        `;
        
        typingElement.id = 'clai-chat-typing-indicator';
        messagesContainer.appendChild(typingElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    },
    
    // Hide typing indicator
    hideTyping: function() {
        this.state.typing = false;
        var typingIndicator = document.getElementById('clai-chat-typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    },
    
    // Connect to WebSocket
    connectWebSocket: function() {
        var self = this;
        var socketUrl = this.state.config.apiUrl;
        
        if (!window.io) {
            console.error('Socket.IO not loaded');
            return;
        }
        
        this.socket = io(socketUrl);
        
        this.socket.on('connect', function() {
            console.log('Connected to WebSocket');
        });
        
        this.socket.on('message', function(data) {
            self.hideTyping();
            self.addMessage(data.content, 'bot');
        });
        
        this.socket.on('typing', function(data) {
            if (data.status === 'started') {
                self.showTyping();
            } else {
                self.hideTyping();
            }
        });
    },
    
    // Start a new conversation
    startConversation: function(message) {
        var self = this;
        
        // Get UTM parameters
        var utmParams = {
            source: this.getParameterByName('utm_source'),
            medium: this.getParameterByName('utm_medium'),
            campaign: this.getParameterByName('utm_campaign')
        };
        
        // API request to start conversation
        fetch(this.state.config.apiUrl + '/api/conversations/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chatbot_id: this.state.config.chatbotId,
                visitor_id: this.getVisitorId(),
                utm_source: utmParams.source,
                utm_medium: utmParams.medium,
                utm_campaign: utmParams.campaign,
                referrer: document.referrer
            })
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            self.state.conversationId = data.conversation_id;
            
            // Join the conversation room
            if (self.socket) {
                self.socket.emit('join', { conversation_id: data.conversation_id });
            }
            
            // Send initial message
            self.sendMessageToServer(message);
        })
        .catch(function(error) {
            console.error('Error starting conversation:', error);
            self.addMessage('Sorry, there was an error connecting to the server. Please try again later.', 'bot');
        });
    },
    
    // Send message to server
    sendMessageToServer: function(message) {
        var self = this;
        
        // Show typing indicator
        this.showTyping();
        
        // Use WebSocket if available
        if (this.socket && this.socket.connected) {
            this.socket.emit('message', {
                conversation_id: this.state.conversationId,
                content: message
            });
            return;
        }
        
        // Fallback to REST API
        fetch(this.state.config.apiUrl + '/api/conversations/' + this.state.conversationId + '/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: message
            })
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            self.hideTyping();
            self.addMessage(data.content, 'bot');
        })
        .catch(function(error) {
            console.error('Error sending message:', error);
            self.hideTyping();
            self.addMessage('Sorry, there was an error processing your message. Please try again later.', 'bot');
        });
    },
    
    // Get URL parameter by name
    getParameterByName: function(name) {
        var url = window.location.href;
        name = name.replace(/[\[\]]/g, '\\$&');
        var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, ' '));
    },
    
    // Get or create visitor ID
    getVisitorId: function() {
        var visitorId = localStorage.getItem('clai_visitor_id');
        if (!visitorId) {
            visitorId = this.generateUUID();
            localStorage.setItem('clai_visitor_id', visitorId);
        }
        return visitorId;
    },
    
    // Generate UUID
    generateUUID: function() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
};
