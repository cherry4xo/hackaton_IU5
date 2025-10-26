import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './app/index';
import { AuthProvider } from './app/providers/AuthProvider'; // <-- 1. Импортируем провайдер
import './app/styles/global.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* 
      Теперь последовательность правильная:
      1. BrowserRouter - для навигации
      2. AuthProvider - для данных пользователя
      3. App - само приложение
    */}
    <BrowserRouter>
      <AuthProvider> {/* <-- 2. Оборачиваем App в AuthProvider */}
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);