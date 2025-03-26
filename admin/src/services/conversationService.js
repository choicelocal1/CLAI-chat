import api from './api';

export const getConversations = async (params) => {
  try {
    const response = await api.get('/api/conversations', { params });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get conversations' };
  }
};

export const getConversation = async (id) => {
  try {
    const response = await api.get(`/api/conversations/${id}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get conversation' };
  }
};

export const endConversation = async (id) => {
  try {
    const response = await api.post(`/api/conversations/${id}/end`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to end conversation' };
  }
};
