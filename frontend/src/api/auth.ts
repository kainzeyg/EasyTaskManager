import apiClient from './client';

export const login = async (email: string, password: string) => {
  const response = await apiClient.post('/auth/login', { email, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};

export const register = async (userData: {
  username: string;
  email: string;
  password: string;
}) => {
  const response = await apiClient.post('/auth/registration', userData);
  return response.data;
};

export const logout = async () => {
  await apiClient.post('/auth/logout');
};