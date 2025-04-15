import apiClient from './client';

export const getProjectTasks = async (projectId: number) => {
  const response = await apiClient.get(`/tasks/list?project_id=${projectId}`);
  return response.data;
};

export const updateTaskStatus = async ({
  taskId,
  status,
}: {
  taskId: number;
  status: string;
}) => {
  const response = await apiClient.post(`/tasks/change/${taskId}`, { status });
  return response.data;
};