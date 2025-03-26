export class ApiService {
  constructor(apiUrl) {
    this.apiUrl = apiUrl;
  }
  
  async startConversation(data) {
    const response = await fetch(`${this.apiUrl}/api/conversations/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to start conversation: ${response.status}`);
    }
    
    return response.json();
  }
  
  async sendMessage(conversationId, content) {
    const response = await fetch(`${this.apiUrl}/api/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.status}`);
    }
    
    return response.json();
  }
  
  async endConversation(conversationId) {
    const response = await fetch(`${this.apiUrl}/api/conversations/${conversationId}/end`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to end conversation: ${response.status}`);
    }
    
    return response.json();
  }
  
  async createLead(data) {
    const response = await fetch(`${this.apiUrl}/api/leads/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create lead: ${response.status}`);
    }
    
    return response.json();
  }
  
  async getWidgetConfig(chatbotId) {
    const response = await fetch(`${this.apiUrl}/widget/${chatbotId}/config`);
    
    if (!response.ok) {
      throw new Error(`Failed to get widget config: ${response.status}`);
    }
    
    return response.json();
  }
}
