
import HomePage from '../pages/HomePage';
import CalculatePage from '../pages/CalculatePage';
import HistoryPage from '../pages/HistoryPage';
import ResultsPage from '../pages/ResultPage';
import { Routes, Route } from 'react-router-dom';
import { MainLayout } from '../widgets/MainLayout/ui/MainLayout';
import React from 'react';

function App() {
  return (
    <Routes>
      {/* 
        MainLayout теперь является "макетом" для дочерних маршрутов.
        Он будет рендериться один раз, а дочерний компонент (HomePage, и т.д.)
        будет вставляться в его <Outlet />.
      */}
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="calculate" element={<CalculatePage />} />
        <Route path="results/:taskId" element={<ResultsPage />} />
      </Route>
    </Routes>
  );
}

export default App;