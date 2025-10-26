// src/features/Auth/Registration.tsx

import React, { useState } from 'react';
import './Registration.css';
import { Button } from '../../shared/ui/Button';
import { Input } from '../../shared/ui/Input';
import { register as apiRegister, login as apiLogin, getMe as apiGetMe } from '../../shared/api/auth';
import { useAuth } from '../../app/providers/AuthProvider';

interface RegistrationProps {
  onClose: () => void;
  onShowLogin: () => void;
}

export const Registration: React.FC<RegistrationProps> = ({ onClose, onShowLogin }) => {
  const { setUser } = useAuth();
  const [email, setEmail] = useState('');
  const [login, setLogin] = useState(''); // Это будет `username`
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const validate = (): boolean => {
    const newErrors: { [key: string]: string } = {};
    if (!/\S+@\S+\.\S+/.test(email)) newErrors.email = 'Некорректный формат почты';
    if (login.trim().length < 4) newErrors.login = 'Имя пользователя должно быть не менее 4 символов';
    if (password.length < 8) newErrors.password = 'Пароль должен быть не менее 8 символов';
    if (password !== confirmPassword) newErrors.confirmPassword = 'Пароли не совпадают';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRegister = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    setFormError(null);
    
    try {
      // 1. Отправляем запрос только на регистрацию
      await apiRegister({ email, username: login, password });
      
      // 2. Показываем сообщение об успехе и переключаем на окно входа
      alert('Вы успешно зарегистрированы! Теперь можете войти.');
      onShowLogin(); 
      
    } catch (err: any) {
      // 3. Ловим ошибку, если она произошла именно при регистрации
      console.error('Ошибка регистрации:', err);
      const errorMessage = err.detail?.[0]?.msg || err.message || 'Произошла ошибка при регистрации';
      setFormError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="registration-modal">
        <button onClick={onClose} className="close-button">×</button>
        <h2 className="registration-title">Регистрация</h2>
    
        <form onSubmit={handleRegister} className="registration-form" noValidate>
          <Input label="Почта" type="email" placeholder="Введите вашу почту" value={email} onChange={(e) => setEmail(e.target.value)} error={errors.email} />
          <Input label="Имя пользователя" type="text" placeholder="Придумайте имя" value={login} onChange={(e) => setLogin(e.target.value)} error={errors.login} />
          <Input label="Пароль" type="password" placeholder="Придумайте пароль" value={password} onChange={(e) => setPassword(e.target.value)} error={errors.password} />
          <Input label="Пароль (повторно)" type="password" placeholder="Повторите пароль" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} error={errors.confirmPassword} />
          
          {formError && <div className="form-error-message">{formError}</div>}
          
          <Button type="submit" size="lg" className="registration-button" disabled={isLoading} loading={isLoading}>
            {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
          </Button>
        </form>
    
        <button type="button" onClick={onShowLogin} className="switch-form-link">
          Уже есть аккаунт? Войти
        </button>
      </div>
    </div>
  );
};