import apiClient from './client';

export const getProjects = async () => {
  const response = await apiClient.get('/projects/list');
  return response.data;
};

export const createProject = async (projectData: {
  name: string;
  periodicity: string;
}) => {
  const response = await apiClient.post('/projects/create', projectData);
  return response.data;
};