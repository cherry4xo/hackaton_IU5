import React, { useState } from 'react';
import './Registration.css';
import { Button } from '../../shared/ui/Button';
import { Input } from '../../shared/ui/Input';
interface RegistrationProps {
onClose: () => void; // Функция для закрытия окна
onShowLogin: () => void; // Функция для переключения обратно на окно входа
}
export const Registration: React.FC<RegistrationProps> = ({ onClose, onShowLogin }) => {
const [email, setEmail] = useState('');
const [login, setLogin] = useState('');
const [password, setPassword] = useState('');
const [confirmPassword, setConfirmPassword] = useState('');
const handleRegister = (event: React.FormEvent) => {
event.preventDefault();
if (password !== confirmPassword) {
alert('Пароли не совпадают!');
return;
}
console.log('Registering with:', { email, login, password });
// Здесь будет логика отправки данных для регистрации
};
return (
<div className="modal-overlay">
    <div className="registration-modal">
    <button onClick={onClose} className="close-button">×</button>
    <h2 className="registration-title">Регистрация</h2>
    
    <form onSubmit={handleRegister} className="registration-form">
      <Input
        label="Почта"
        type="email"
        placeholder="Введите вашу почту"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <Input
        label="Логин"
        type="text"
        placeholder="Придумайте логин"
        value={login}
        onChange={(e) => setLogin(e.target.value)}
        required
      />
      <Input
        label="Пароль"
        type="password"
        placeholder="Придумайте пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <Input
        label="Пароль (повторно)"
        type="password"
        placeholder="Повторите пароль"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
      />

      <Button type="submit" size="lg" className="registration-button">
        Зарегистрироваться
      </Button>
    </form>
    
    <button type="button" onClick={onShowLogin} className="switch-form-link">
      Уже есть аккаунт? Войти
    </button>
  </div>
</div>
);
};