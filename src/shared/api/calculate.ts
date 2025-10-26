import { BASE_URL, checkResponse } from './config';

interface ObservationData { time: string; ra: string; dec: string; }

// Функция-помощник для запросов, требующих токен
const fetchWithAuth = (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('accessToken');
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
  };
  return fetch(url, { ...options, headers }).then(checkResponse);
};

// Запрос на ЗАГРУЗКУ ИЗОБРАЖЕНИЯ (теперь требует токен)
export const uploadImage = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  return fetchWithAuth(`${BASE_URL}/orbit/upload-image`, {
    method: 'POST',
    body: formData,
  });
};

// Запрос на РАСЧЕТ ОРБИТЫ (теперь требует токен)
export const calculateOrbit = (data: {
  observations: ObservationData[];
  cometName: string;
  imageIds: string[];
}) => {
  return fetchWithAuth(`${BASE_URL}/orbit/calculate`, { // <-- Замените на реальный URL, когда он будет
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
};