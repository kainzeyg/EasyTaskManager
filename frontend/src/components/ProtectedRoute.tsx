import { Navigate, Outlet } from 'react-router-dom';

import Loader from './ui/Loader'; // Предполагается, что у вас есть компонент Loader
import { useAuth } from '../hooks/useAuth';
const ProtectedRoute = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <Loader />; // Показываем лоадер во время проверки авторизации
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/auth" replace />;
};

export default ProtectedRoute;