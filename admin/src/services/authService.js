import api from './api';

export const login = async (email, password) => {
  try {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Login failed' };
  }
};

export const register = async (userData) => {
  try {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Registration failed' };
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get('/api/users/me');
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get user info' };
  }
};
