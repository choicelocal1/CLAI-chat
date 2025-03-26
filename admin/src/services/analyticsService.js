import api from './api';

export const getOverviewAnalytics = async (params) => {
  try {
    const response = await api.get('/api/analytics/overview', { params });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get analytics overview' };
  }
};

export const getLeadAnalytics = async (params) => {
  try {
    const response = await api.get('/api/analytics/leads', { params });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get lead analytics' };
  }
};

export const getSourceAnalytics = async (params) => {
  try {
    const response = await api.get('/api/analytics/sources', { params });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get source analytics' };
  }
};

export const getTimeAnalytics = async (params) => {
  try {
    const response = await api.get('/api/analytics/time', { params });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get time analytics' };
  }
};

export const getEfficiencyAnalytics = async (params) => {
  try {
    const response = await api.get('/api/analytics/efficiency', { params });
    return response.data;
  } catch (error) {
    throw error.response?.data || { error: 'Failed to get efficiency analytics' };
  }
};
