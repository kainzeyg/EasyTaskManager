import { useMutation, useQuery } from '@tanstack/react-query';
import { login, register, logout, getCurrentUser } from '../api/auth';
import { useNavigate } from 'react-router-dom';

export const useAuth = () => {
  const navigate = useNavigate();
  
  // Добавляем запрос для проверки текущего пользователя
  const { data: user, isLoading: isCheckingAuth } = useQuery(
    ['currentUser'],
    getCurrentUser,
    {
      enabled: !!localStorage.getItem('access_token'),
      retry: false,
    }
  );

  const loginMutation = useMutation(login, {
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      navigate('/dashboard');
    },
  });

  const registerMutation = useMutation(register, {
    onSuccess: () => {
      navigate('/auth?tab=login');
    },
  });

  const logoutMutation = useMutation(logout, {
    onSuccess: () => {
      localStorage.removeItem('access_token');
      navigate('/auth');
    },
  });

  return {
    user,
    isAuthenticated: !!user,
    isLoading: loginMutation.isLoading || registerMutation.isLoading || isCheckingAuth,
    error: loginMutation.error || registerMutation.error,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,
  };
};