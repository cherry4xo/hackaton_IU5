// src/shared/api/auth.ts

import { BASE_URL, checkResponse } from './config';

// Типы данных для запросов
interface RegisterData {
  email: string;
  username: string;
  password?: string;
}

interface LoginData {
  username: string; // Это будет почта пользователя
  password?: string;
}

// 1. ЗАПРОС НА РЕГИСТРАЦИЮ
// POST /users/
export const register = (data: RegisterData) => {
  return fetch(`${BASE_URL}/users/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  }).then(checkResponse);
};

// 2. ЗАПРОС НА ВХОД (ПОЛУЧЕНИЕ ТОКЕНА)
// POST /users/access-token
export const login = (data: LoginData) => {
  const formBody = new URLSearchParams();
  formBody.append('username', data.username);
  if (data.password) {
    formBody.append('password', data.password);
  }

  return fetch(`${BASE_URL}/users/access-token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formBody.toString(),
  }).then(checkResponse);
};

// 3. ЗАПРОС НА ПОЛУЧЕНИЕ ДАННЫХ О СЕБЕ
// GET /users/me
export const getMe = (token: string) => {
  return fetch(`${BASE_URL}/users/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  }).then(checkResponse);
};