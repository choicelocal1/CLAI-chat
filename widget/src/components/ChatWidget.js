import { createDOM } from '../utils/dom';
import { SocketService } from '../utils/SocketService';
import { ApiService } from '../utils/ApiService';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ChatHeader } from './ChatHeader';
import { LeadForm } from './LeadForm';
import { StorageService } from '../utils/StorageService';

export class ChatWidget {
  constructor(config) {
    this.config = config;
    this.state = {
      isOpen: false,
      messages: [],
      typing: false,
      conversationId: null,
      visitorId: StorageService.getVisitorId(),
      leadFormActive: false,
      leadInfo: {}
    };
    
    this.elements = {};
    this.apiService = new ApiService(config.apiUrl);
    this.socketService = new SocketService(config.apiUrl);
    
    // Bind methods
    this.toggleChat = this.toggleChat.bind(this);
    this.sendMessage = this.sendMessage.bind(this);
    this.addMessage = this.addMessage.bind(this);
    this.handleTypingStatus = this.handleTypingStatus.bind(this);
    this.handleBotMessage = this.handleBotMessage.bind(this);
    this.handleLeadSubmit = this.handleLeadSubmit.bind(this);
    
    // Set up socket event listeners
    this.setupSocketListeners();
  }
  
  render() {
    const container = document.getElementById(this.config.containerId);
    if (!container) return;
    
    // Create main widget container
    const widget = createDOM('div', { id: 'clai-chat-widget' });
    
    // Create launcher button
    const launcher = createDOM('div', { 
      className: 'clai-chat-launcher',
      innerHTML: `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z" fill="white"/>
        </svg>
      `,
      onClick: this.toggleChat
    });
    
    // Create chat window
    const chatWindow = createDOM('div', { className: 'clai-chat-window' });
    
    // Create chat components
    const header = new ChatHeader({
      title: this.config.name,
      onClose: this.toggleChat
    });
    
    const messageList = new MessageList();
    const chatInput = new ChatInput({ onSend: this.sendMessage });
    
    // Add components to chat window
    chatWindow.appendChild(header.element);
    chatWindow.appendChild(messageList.element);
    chatWindow.appendChild(chatInput.element);
    
    // Add to widget
    widget.appendChild(launcher);
    widget.appendChild(chatWindow);
    
    // Add to container
    container.appendChild(widget);
    
    // Store elements for later use
    this.elements = {
      widget,
      launcher,
      chatWindow,
      header: header.element,
      messageList: messageList.element,
      chatInput: chatInput.element
    };
    
    // Add welcome message
    this.addMessage({
      content: "Hi there! 👋 How can I help you today?",
      sender: "bot"
    });
  }
  
  toggleChat() {
    this.state.isOpen = !this.state.isOpen;
    
    if (this.state.isOpen) {
      this.elements.chatWindow.classList.add('active');
      // Focus input when opening
      setTimeout(() => {
        const input = this.elements.chatInput.querySelector('input');
        if (input) input.focus();
      }, 300);
    } else {
      this.elements.chatWindow.classList.remove('active');
    }
  }
  
  sendMessage(message) {
    if (!message.trim()) return;
    
    // Add message to UI
    this.addMessage({
      content: message,
      sender: 'human'
    });
    
    // Start conversation if needed
    if (!this.state.conversationId) {
      this.startConversation(message);
    } else {
      this.socketService.sendMessage(this.state.conversationId, message);
    }
  }
  
  async startConversation(message) {
    try {
      // Get UTM parameters
      const utmParams = {
        source: this.getParameterByName('utm_source'),
        medium: this.getParameterByName('utm_medium'),
        campaign: this.getParameterByName('utm_campaign')
      };
      
      const response = await this.apiService.startConversation({
        chatbot_id: this.config.chatbotId,
        visitor_id: this.state.visitorId,
        utm_source: utmParams.source,
        utm_medium: utmParams.medium,
        utm_campaign: utmParams.campaign,
        referrer: document.referrer
      });
      
      this.state.conversationId = response.conversation_id;
      
      // Join conversation room
      this.socketService.joinConversation(this.state.conversationId);
      
      // Send initial message
      this.socketService.sendMessage(this.state.conversationId, message);
    } catch (error) {
      console.error('Error starting conversation:', error);
      this.addMessage({
        content: 'Sorry, there was an error connecting to the server. Please try again later.',
        sender: 'bot'
      });
    }
  }
  
  setupSocketListeners() {
    this.socketService.onTyping(this.handleTypingStatus);
    this.socketService.onMessage(this.handleBotMessage);
  }
  
  handleTypingStatus(status) {
    if (status === 'started') {
      this.showTypingIndicator();
    } else {
      this.hideTypingIndicator();
    }
  }
  
  handleBotMessage(message) {
    this.hideTypingIndicator();
    this.addMessage({
      content: message.content,
      sender: 'bot'
    });
    
    // Check if this is a lead capture prompt
    if (this.shouldShowLeadForm(message.content)) {
      this.showLeadForm();
    }
  }
  
  shouldShowLeadForm(message) {
    // Simple heuristic - could be much more sophisticated
    const leadTriggers = [
      'email address',
      'contact information',
      'reach out',
      'get in touch',
      'provide your'
    ];
    
    return leadTriggers.some(trigger => 
      message.toLowerCase().includes(trigger.toLowerCase())
    );
  }
  
  showLeadForm() {
    if (this.state.leadFormActive) return;
    
    this.state.leadFormActive = true;
    
    // Create lead form
    const leadForm = new LeadForm({
      onSubmit: this.handleLeadSubmit,
      fields: this.config.leadCapture?.fields || ['name', 'email', 'phone']
    });
    
    // Add to message list
    this.elements.messageList.appendChild(leadForm.element);
    
    // Scroll to bottom
    this.elements.messageList.scrollTop = this.elements.messageList.scrollHeight;
  }
  
  async handleLeadSubmit(leadInfo) {
    try {
      // Save lead information
      this.state.leadInfo = leadInfo;
      
      // Submit lead to server
      await this.apiService.createLead({
        organization_id: this.config.organizationId,
        conversation_id: this.state.conversationId,
        name: leadInfo.name,
        email: leadInfo.email,
        phone: leadInfo.phone,
        utm_source: this.getParameterByName('utm_source'),
        utm_medium: this.getParameterByName('utm_medium'),
        utm_campaign: this.getParameterByName('utm_campaign')
      });
      
      // Remove lead form
      this.state.leadFormActive = false;
      
      // Add confirmation message
      this.addMessage({
        content: 'Thank you! Your information has been submitted.',
        sender: 'bot'
      });
      
      // Resume conversation
      this.socketService.sendMessage(
        this.state.conversationId, 
        `I've submitted my information. My name is ${leadInfo.name} and my email is ${leadInfo.email}.`
      );
    } catch (error) {
      console.error('Error submitting lead:', error);
      this.addMessage({
        content: 'Sorry, there was an error submitting your information. Please try again later.',
        sender: 'bot'
      });
    }
  }
  
  addMessage(message) {
    // Create message element
    const messageElement = createDOM('div', { 
      className: `clai-chat-message ${message.sender}`,
      innerText: message.content
    });
    
    // Add to message list
    this.elements.messageList.appendChild(messageElement);
    
    // Scroll to bottom
    this.elements.messageList.scrollTop = this.elements.messageList.scrollHeight;
    
    // Add to messages array
    this.state.messages.push({
      ...message,
      timestamp: new Date()
    });
  }
  
  showTypingIndicator() {
    if (this.state.typing) return;
    
    this.state.typing = true;
    
    // Create typing indicator
    const typingElement = createDOM('div', {
      className: 'clai-chat-typing',
      id: 'clai-chat-typing-indicator',
      innerHTML: `
        <div class="clai-chat-typing-bubble"></div>
        <div class="clai-chat-typing-bubble"></div>
        <div class="clai-chat-typing-bubble"></div>
      `
    });
    
    // Add to message list
    this.elements.messageList.appendChild(typingElement);
    
    // Scroll to bottom
    this.elements.messageList.scrollTop = this.elements.messageList.scrollHeight;
  }
  
  hideTypingIndicator() {
    this.state.typing = false;
    
    // Remove typing indicator
    const typingIndicator = document.getElementById('clai-chat-typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }
  
  getParameterByName(name) {
    const url = window.location.href;
    name = name.replace(/[\[\]]/g, '\\$&');
    const regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
          results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
  }
}
