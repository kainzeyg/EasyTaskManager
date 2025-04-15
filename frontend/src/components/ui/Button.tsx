import { ReactNode } from 'react';

interface ButtonProps {
  children: ReactNode;
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
  className?: string;
  onClick?: () => void;
}

const Button = ({ 
  children, 
  type = 'button', 
  disabled = false, 
  className = '', 
  onClick 
}: ButtonProps) => {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`px-4 py-2 rounded-md bg-primary text-white hover:bg-primary-dark disabled:opacity-50 ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;