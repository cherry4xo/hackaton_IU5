import React from 'react';
import styles from '../Input/Input.module.css';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  className?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  type = 'text',
  className = '',
  error,
  ...props
}) => {
  const inputId = React.useId();

  return (
    <div className={`${styles.inputContainer} ${className}`}>
      <label htmlFor={inputId} className={styles.label}>
        {label}
      </label>
      <input
        id={inputId}
        type={type}
        className={`${styles.input} ${error ? styles.errorInput : ''}`}
        {...props}
      />
      {error && <span className={styles.errorMessage}>{error}</span>}
    </div>
  );
};