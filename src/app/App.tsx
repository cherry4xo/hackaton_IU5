import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { MainLayout } from '../widgets/MainLayout/ui/MainLayout';
import HomePage from '../pages/HomePage';
import CalculatePage from '../pages/CalculatePage';
import ResultsPage from '../pages/ResultsPage';
import ProfilePage from '../pages/ProfilePage';
import { ProjectsPage } from '../pages/ProjectsPage';
import LibraryPage from '../pages/LibraryPage'; // Создадим

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="calculate" element={<CalculatePage />} />
        <Route path="results" element={<ResultsPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="projects" element={<ProjectsPage />} />
        <Route path="library" element={<LibraryPage />} />
      </Route>
    </Routes>
  );
}

export default App;