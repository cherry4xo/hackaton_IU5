
import React, { useState } from 'react';
import './Login.css';
import { Button } from '../../shared/ui/Button';
import { Input } from '../../shared/ui/Input';

interface LoginProps {
  onClose: () => void;
  onShowRegister: () => void;
}

export const Login: React.FC<LoginProps> = ({ onClose, onShowRegister }) => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const validate = (): boolean => {
    const newErrors: { [key: string]: string } = {};
    
    if (!login.trim()) {
      newErrors.login = 'Логин не может быть пустым';
    }
    if (!password) {
      newErrors.password = 'Пароль не может быть пустым';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = (event: React.FormEvent) => {
    event.preventDefault();
    if (!validate()) {
      return;
    }
    setErrors({});
    console.log('Logging in with:', { login, password });
  };

  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="login-modal">
        <button onClick={onClose} className="close-button">×</button>
        <h2 className="login-title">Вход</h2>
        
        <form onSubmit={handleLogin} className="login-form" noValidate> 
          <Input
            label="Логин"
            type="text"
            placeholder="Введите логин"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            error={errors.login}
          />
          <div className="password-container">
            <Input
              label="Пароль"
              type="password"
              placeholder="Введите пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={errors.password}
            />
            <a href="#" className="forgot-password-link">Забыли пароль?</a>
          </div>
          <Button type="submit" size="lg" className="login-button">
            Войти
          </Button>
        </form>
        
        <button type="button" onClick={onShowRegister} className="register-link">
          Зарегистрироваться
        </button>
      </div>
    </div>
  );
};