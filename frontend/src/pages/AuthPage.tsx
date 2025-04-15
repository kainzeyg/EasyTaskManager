import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';       // default import
import RegisterForm from '../components/auth/RegisterForm'; // default import

const AuthPage = () => {
  const [searchParams] = useSearchParams();
  const tab = searchParams.get('tab') || 'login';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">
          {tab === 'login' ? 'Вход' : 'Регистрация'}
        </h1>
        {tab === 'login' ? <LoginForm /> : <RegisterForm />}
      </div>
    </div>
  );
};

export default AuthPage;