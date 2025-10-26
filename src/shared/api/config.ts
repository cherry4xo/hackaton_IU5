// Здесь будет базовый URL вашего бэкенда.
// Мы используем переменные окружения, чтобы легко менять его для разработки и продакшена.
export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

// Общая функция-обертка для проверки ответа от сервера
export const checkResponse = (res: Response) => {
  if (res.ok) {
    return res.json();
  }
  // Если сервер вернул ошибку, пытаемся извлечь сообщение
  return res.json().then((err) => Promise.reject(err));
};