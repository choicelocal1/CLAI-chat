import { createDOM } from '../utils/dom';

export class ChatHeader {
  constructor(options) {
    this.title = options.title;
    this.onClose = options.onClose;
    
    this.element = this.render();
  }
  
  render() {
    const header = createDOM('div', { className: 'clai-chat-header' });
    
    const title = createDOM('div', { 
      className: 'clai-chat-title',
      innerText: this.title
    });
    
    const closeButton = createDOM('div', {
      className: 'clai-chat-close',
      innerText: '×',
      onClick: this.onClose
    });
    
    header.appendChild(title);
    header.appendChild(closeButton);
    
    return header;
  }
}
