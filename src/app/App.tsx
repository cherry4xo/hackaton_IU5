import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { MainLayout } from '../widgets/MainLayout/ui/MainLayout';
import HomePage from '../pages/HomePage';
import CalculatePage from '../pages/CalculatePage';
import HistoryPage from '../pages/HistoryPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="history" element={<HistoryPage />} />;
        <Route path="calculate" element={<CalculatePage />} />
      </Route>
    </Routes>
  );
}

export default App;