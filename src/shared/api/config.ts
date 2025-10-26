// Здесь будет базовый URL вашего бэкенда.
// Мы используем переменные окружения, чтобы легко менять его для разработки и продакшена.
export const BASE_URL = import.meta.env.VITE_API_URL || 'https://api.cherry4xo.ru/backend';

export const checkResponse = (res: Response) => {
  // Проверяем, есть ли у ответа тело (body) для парсинга
  const contentType = res.headers.get('content-type');
  if (res.status === 204 || contentType === null) { // 204 No Content или полное отсутствие тела
    return Promise.resolve(null); // Возвращаем null, если тело пустое
  }

  // Если тело есть, пытаемся распарсить его как JSON
  if (contentType && contentType.includes('application/json')) {
    if (res.ok) {
      return res.json();
    }
    // Если статус не ok, но тело в JSON (ошибка валидации), возвращаем ошибку
    return res.json().then((err) => Promise.reject(err));
  }

  // Если ответ не JSON, но успешный (например, для файлов)
  if (res.ok) {
    return res.text(); // Или res.blob() в зависимости от эндпоинта
  }
  
  // Для всех остальных ошибок
  return Promise.reject(`Ошибка: ${res.status}`);
};