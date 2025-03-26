import { createDOM } from '../utils/dom';

export class MessageList {
  constructor() {
    this.element = this.render();
  }
  
  render() {
    return createDOM('div', { className: 'clai-chat-messages' });
  }
}
