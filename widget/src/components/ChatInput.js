import { createDOM } from '../utils/dom';

export class ChatInput {
  constructor(options) {
    this.onSend = options.onSend;
    this.element = this.render();
    this.inputElement = this.element.querySelector('input');
  }
  
  render() {
    const inputArea = createDOM('div', { className: 'clai-chat-input-area' });
    
    const input = createDOM('input', {
      className: 'clai-chat-input',
      placeholder: 'Type a message...',
      onKeypress: (e) => {
        if (e.key === 'Enter') {
          this.handleSend();
        }
      }
    });
    
    const sendButton = createDOM('button', {
      className: 'clai-chat-send',
      onClick: () => this.handleSend(),
      innerHTML: `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z" fill="white"/>
        </svg>
      `
    });
    
    inputArea.appendChild(input);
    inputArea.appendChild(sendButton);
    
    return inputArea;
  }
  
  handleSend() {
    const message = this.inputElement.value.trim();
    
    if (message) {
      this.onSend(message);
      this.inputElement.value = '';
    }
  }
}
