import jwtDecode from 'jwt-decode';

export const getStoredToken = () => {
  return localStorage.getItem('auth_token');
};

export const isTokenValid = (token) => {
  try {
    const decoded = jwtDecode(token);
    return decoded.exp * 1000 > Date.now();
  } catch (error) {
    return false;
  }
};

export const getAuthHeaders = () => {
  const token = getStoredToken();
  return {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  };
};
