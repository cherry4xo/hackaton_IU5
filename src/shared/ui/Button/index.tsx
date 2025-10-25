// shared/ui/Button/index.tsx
import React from 'react';
import styles from './Button.module.css';

export interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  loading?: boolean;
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  type = 'button',
  loading = false,
  className = '',
}) => {
  const handleClick = () => {
    if (!disabled && !loading && onClick) {
      onClick();
    }
  };

  return (
    <button
      type={type}
      className={`
        ${styles.button} 
        ${styles[variant]} 
        ${styles[size]} 
        ${disabled ? styles.disabled : ''}
        ${loading ? styles.loading : ''}
        ${className}
      `}
      onClick={handleClick}
      disabled={disabled || loading}
    >
      {loading && <span className={styles.spinner} />}
      {children}
    </button>
  );
};