import { BASE_URL, checkResponse } from './config';

interface RegisterData { email: string; username: string; password?: string; }
interface LoginData { username: string; password?: string; } // `username` - это почта

export const register = (data: RegisterData) => { /* ... как и раньше ... */ };

// Запрос на ВХОД, теперь он использует email как username
export const login = (data: LoginData) => {
  const formBody = new URLSearchParams();
  formBody.append('username', data.username);
  if (data.password) formBody.append('password', data.password);

  return fetch(`${BASE_URL}/users/access-token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formBody.toString(),
  }).then(checkResponse);
};

// Запрос на получение данных о себе
export const getMe = (token: string) => {
  return fetch(`${BASE_URL}/users/me`, {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${token}` },
  }).then(checkResponse);
};