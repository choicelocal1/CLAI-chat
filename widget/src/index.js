import './styles/main.scss';
import { ChatWidget } from './components/ChatWidget';

// Create global namespace
window.CLAIChat = window.CLAIChat || {};

// Initialize function for external use
window.CLAIChat.init = function(config) {
  const widget = new ChatWidget(config);
  widget.render();
  
  // Store instance for potential external access
  window.CLAIChat.instance = widget;
  
  return widget;
};

// For local development and testing
if (process.env.NODE_ENV === 'development') {
  window.CLAIChat.init({
    containerId: 'chat-widget-container',
    chatbotId: '1',
    apiUrl: 'http://localhost:5000',
    name: 'Test Bot',
    theme: {
      primaryColor: '#0088CC',
      textColor: '#333333',
      position: 'right'
    }
  });
}
