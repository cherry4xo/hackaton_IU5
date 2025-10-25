import React, { useState } from 'react';
import './Login.css';
import { Button } from '../../shared/ui/Button';
import { Input } from '../../shared/ui/Input';

interface LoginProps {
  onClose: () => void;
  onShowRegister: () => void; // Новая функция для переключения на регистрацию
}

export const Login: React.FC<LoginProps> = ({ onClose, onShowRegister }) => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (event: React.FormEvent) => {
    event.preventDefault();
    console.log('Logging in with:', { login, password });
  };

  return (
    <div className="modal-overlay">
      <div className="login-modal">
        <button onClick={onClose} className="close-button">×</button>
        
        <h2 className="login-title">Вход</h2>
        
        <form onSubmit={handleLogin} className="login-form">
          <Input
            label="Логин"
            type="text"
            placeholder="Введите логин"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            required
          />
          <div className="password-container">
            <Input
              label="Пароль"
              type="password"
              placeholder="Введите пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <a href="#" className="forgot-password-link">Забыли пароль?</a>
          </div>
          <Button type="submit" size="lg" className="login-button">
            Войти
          </Button>
        </form>
        
        {/* ИЗМЕНЕНИЕ: превращаем ссылку в кнопку, вызывающую onShowRegister */}
        <button type="button" onClick={onShowRegister} className="register-link">
          Зарегистрироваться
        </button>
      </div>
    </div>
  );
};