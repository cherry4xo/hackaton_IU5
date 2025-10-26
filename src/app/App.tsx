// src/app/App.tsx

import React from 'react';
import { Routes, Route } from 'react-router-dom';

// 1. Импортируем ОБА лэйаута
import { MainLayout } from '../widgets/MainLayout/ui/MainLayout';
import { DarkLayout } from '../widgets/DarkLayout/ui/DarkLayout'; // <-- ДОБАВЬТЕ ЭТОТ ИМПОРТ

// Импортируем страницы
import HomePage from '../pages/HomePage';
import CalculatePage from '../pages/CalculatePage';
import HistoryPage from '../pages/HistoryPage';
import ResultsPage from '@/pages/ResultPage';


function App() {
  return (
    <Routes>
<<<<<<< HEAD
      {/* ГРУППА 1: Страницы, использующие MainLayout (синий фон) */}
      <Route element={<MainLayout />}>
        <Route path="/" element={<HomePage />} />
        {/* Сюда можно добавить другие страницы с синим фоном */}
      </Route>

      {/* ГРУППА 2: Страницы, использующие DarkLayout (темный фон) */}
      <Route element={<DarkLayout />}>
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/calculate" element={<CalculatePage />} />
        {/* Сюда вы будете добавлять новые страницы с темным фоном */}
=======
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="calculate" element={<CalculatePage />} />
        
        {/* --- 2. ДОБАВЬТЕ ЭТОТ МАРШРУТ --- */}
        {/* :taskId - это динамический параметр, который мы будем получать из URL */}
        <Route path="results/:taskId" element={<ResultsPage />} />
        
>>>>>>> d12ac1af4a023cb667de6be9863c869c4e9c889c
      </Route>
    </Routes>
  );
}

export default App;