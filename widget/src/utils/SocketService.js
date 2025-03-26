import io from 'socket.io-client';

export class SocketService {
  constructor(apiUrl) {
    this.socket = null;
    this.apiUrl = apiUrl;
    this.connected = false;
    
    this.connect();
  }
  
  connect() {
    try {
      this.socket = io(this.apiUrl);
      
      this.socket.on('connect', () => {
        this.connected = true;
        console.log('Socket connected');
      });
      
      this.socket.on('disconnect', () => {
        this.connected = false;
        console.log('Socket disconnected');
      });
      
      this.socket.on('error', (error) => {
        console.error('Socket error:', error);
      });
    } catch (error) {
      console.error('Failed to connect socket:', error);
    }
  }
  
  joinConversation(conversationId) {
    if (!this.connected) {
      console.warn('Socket not connected, attempting to reconnect');
      this.connect();
    }
    
    this.socket.emit('join', { conversation_id: conversationId });
  }
  
  sendMessage(conversationId, content) {
    if (!this.connected) {
      console.warn('Socket not connected, attempting to reconnect');
      this.connect();
    }
    
    this.socket.emit('message', {
      conversation_id: conversationId,
      content: content
    });
  }
  
  onMessage(callback) {
    this.socket.on('message', callback);
  }
  
  onTyping(callback) {
    this.socket.on('typing', (data) => {
      callback(data.status);
    });
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
}
