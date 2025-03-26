export class StorageService {
  static getVisitorId() {
    let visitorId = localStorage.getItem('clai_visitor_id');
    
    if (!visitorId) {
      visitorId = this.generateUUID();
      localStorage.setItem('clai_visitor_id', visitorId);
    }
    
    return visitorId;
  }
  
  static generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
  
  static saveConversation(conversationId) {
    localStorage.setItem('clai_conversation_id', conversationId);
  }
  
  static getConversation() {
    return localStorage.getItem('clai_conversation_id');
  }
}
