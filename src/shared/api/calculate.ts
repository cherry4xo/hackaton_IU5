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


export const calculateClosestApproach = (data: {
  orbit_id: string;
  observation_start_time: string; // <-- Добавлено
  observation_end_time: string;   // <-- Добавлено
}) => {
  const requestBody = {
    orbit_id: data.orbit_id,
    observation_start_time: data.observation_start_time, // <-- Добавлено
    observation_end_time: data.observation_end_time,   // <-- Добавлено
    options: {},
  };

  return fetchWithAuth(`${BASE_URL}/orbit/calculate-closest-approach`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  });
};
export const getTaskResult = (taskId: string) => {
  return fetchWithAuth(`${BASE_URL}/orbit/task/${taskId}/result`);
};