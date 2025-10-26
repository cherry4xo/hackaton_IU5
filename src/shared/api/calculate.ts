// src/shared/api/calculate.ts

import { BASE_URL, checkResponse } from './config';

// Тип для данных наблюдений, как их ожидает бэкенд
interface BackendObservation {
    observation_time: string;
    ra: number;
    dec: number;
}

// 1. ФУНКЦИЯ-ПОМОЩНИК для авторизованных запросов
const fetchWithAuth = (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    return Promise.reject(new Error('Пользователь не авторизован'));
  }
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
  };
  return fetch(url, { ...options, headers }).then(checkResponse);
};


// 2. ЗАПРОС НА РАСЧЕТ ОРБИТЫ
// POST /orbit/calculate
export const calculateOrbit = (data: {
  observations: BackendObservation[];
  image_reference: string | null;
  comet_uuid?: string | null; // <-- Указываем, что это поле необязательное
}) => {
  const url = new URL(`${BASE_URL}/orbit/calculate`);
  
  // --- ИЗМЕНЕНИЕ: Добавляем параметр в URL, ТОЛЬКО ЕСЛИ он был передан ---
  if (data.comet_uuid) {
    url.searchParams.append('comet_uuid', data.comet_uuid);
  }

  const requestBody = {
    observations: data.observations,
    image_reference: data.image_reference || "",
    options: {},
  };

  return fetchWithAuth(url.toString(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });
};


// --- НОВАЯ ФУНКЦИЯ ---
// 3. ЗАПРОС НА РАСЧЕТ СБЛИЖЕНИЯ
// POST /orbit/calculate-closest-approach
export const calculateClosestApproach = (data: {
  orbit_id: string;
}) => {
  const requestBody = {
    orbit_id: data.orbit_id,
    options: {}, // Отправляем пустой объект, как в документации
  };

  return fetchWithAuth(`${BASE_URL}/orbit/calculate-closest-approach`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });
};