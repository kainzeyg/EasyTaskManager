import { useQuery, useMutation } from '@tanstack/react-query';
import { getProjects, createProject } from '../api/projects';

export const useProjects = () => {
  const projectsQuery = useQuery(['projects'], getProjects);
  
  const createMutation = useMutation(createProject, {
    onSuccess: () => {
      projectsQuery.refetch();
    },
  });

  return {
    projects: projectsQuery.data || [],
    isLoading: projectsQuery.isLoading,
    error: projectsQuery.error,
    createProject: createMutation.mutate,
  };
};