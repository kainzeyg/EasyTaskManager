import { Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Header from './ui/Header';

const Layout = () => {
  const { logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <Header onLogout={logout} />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;