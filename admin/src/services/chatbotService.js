import api from './api';

export const getChatBots = async (organizationId) => {
  try {
    const response = await api.get('/api/chatbots', {
      params: { organization_id: organizationId }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get chatbots' };
  }
};

export const getChatBot = async (id) => {
  try {
    const response = await api.get(`/api/chatbots/${id}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get chatbot' };
  }
};

export const createChatBot = async (data) => {
  try {
    const response = await api.post('/api/chatbots', data);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to create chatbot' };
  }
};

export const updateChatBot = async (id, data) => {
  try {
    const response = await api.put(`/api/chatbots/${id}`, data);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to update chatbot' };
  }
};

export const deleteChatBot = async (id) => {
  try {
    const response = await api.delete(`/api/chatbots/${id}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to delete chatbot' };
  }
};

export const cloneChatBot = async (id, data) => {
  try {
    const response = await api.post(`/api/chatbots/${id}/clone`, data);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to clone chatbot' };
  }
};

export const getEmbedCode = async (id) => {
  try {
    const response = await api.get(`/api/chatbots/${id}/embed-code`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get embed code' };
  }
};
