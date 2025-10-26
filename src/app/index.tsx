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

function App() {
  return (
    <Routes>
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
      </Route>
    </Routes>
  );
}

export default App;