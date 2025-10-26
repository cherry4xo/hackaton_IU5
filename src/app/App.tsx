import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { MainLayout } from '../widgets/MainLayout/ui/MainLayout';
import HomePage from '../pages/HomePage';
import CalculatePage from '../pages/CalculatePage';
import HistoryPage from '../pages/HistoryPage';
import ResultsPage from '@/pages/ResultPage';


function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="calculate" element={<CalculatePage />} />
        
        {/* --- 2. ДОБАВЬТЕ ЭТОТ МАРШРУТ --- */}
        {/* :taskId - это динамический параметр, который мы будем получать из URL */}
        <Route path="results/:taskId" element={<ResultsPage />} />
        
      </Route>
    </Routes>
  );
}

export default App;