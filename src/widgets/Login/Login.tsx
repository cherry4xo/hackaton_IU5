
import React, { useState } from 'react';
import './Login.css';
import { Button } from '../../shared/ui/Button';
import { Input } from '../../shared/ui/Input';
import { login as apiLogin, getMe as apiGetMe } from '../../shared/api/auth';
// --- ИСПРАВЛЕНИЕ №2: Импортируем хук useAuth ---
import { useAuth } from '../../app/providers/AuthProvider';

interface LoginProps {
  onClose: () => void;
  onShowRegister: () => void;
}

export const Login: React.FC<LoginProps> = ({ onClose, onShowRegister }) => {
  // --- ИСПРАВЛЕНИЕ №3: Получаем setUser из контекста ---
  const { setUser } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // Состояния для ошибок и загрузки
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // ИЗМЕНЕНИЕ 2: Обновлена логика валидации для почты
  const validate = (): boolean => {
    const newErrors: { [key: string]: string } = {};
    
    if (!email.trim()) {
      newErrors.email = 'Почта не может быть пустой';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Некорректный формат почты';
    }
    if (!password) {
      newErrors.password = 'Пароль не может быть пустым';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ИЗМЕНЕНИЕ 3: Обновлена функция отправки, теперь она работает с бэкендом
 // ЗАМЕНИТЕ ВАШУ ФУНКЦИЮ НА ЭТУ:

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!validate()) return;
    
    setIsLoading(true);
    setFormError(null);

    // --- НАЧАЛО РАБОЧЕГО БЛОКА ---
    // Этот код теперь будет отправлять реальный запрос на сервер
    try {
      // 1. Отправляем запрос на получение токена, используя email как username
      const tokenData = await apiLogin({ username: email, password });
      
      console.log('Успешный вход');
      
      // 2. Сохраняем токен в localStorage, чтобы он был доступен после перезагрузки
      localStorage.setItem('accessToken', tokenData.access_token);
      
      // 3. Получаем данные пользователя с помощью нового токена
      const userData = await apiGetMe(tokenData.access_token);
      
      // 4. Сохраняем пользователя в глобальном состоянии (контексте)
      setUser(userData);

      // 5. Закрываем модальное окно после успешного входа
      onClose();

    } catch (err: any) {
      console.error('Ошибка входа:', err);
      // Показываем пользователю ошибку, которую вернул бэкенд
      setFormError(err.detail || err.message || 'Неверная почта или пароль');
    } finally {
      setIsLoading(false); // Выключаем загрузку в любом случае
    }
    // --- КОНЕЦ РАБОЧЕГО БЛОКА ---
  };
  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="login-modal">
        <button onClick={onClose} className="close-button">×</button>
        <h2 className="login-title">Вход</h2>
        
        <form onSubmit={handleLogin} className="login-form" noValidate> 
          {/* ИЗМЕНЕНИЕ 4: Заменены тексты и привязки для поля почты */}
          <Input
            label="Почта"
            type="email"
            placeholder="Введите почту"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={errors.email}
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
          
          {/* Отображение общей ошибки от сервера */}
          {formError && <div className="form-error-message">{formError}</div>}

          <Button type="submit" size="lg" className="login-button" disabled={isLoading} loading={isLoading}>
            {isLoading ? 'Вход...' : 'Войти'}
          </Button>
        </form>
        
        <button type="button" onClick={onShowRegister} className="register-link">
          Зарегистрироваться
        </button>
      </div>
    </div>
  );
};