import React, { useState, Suspense } from 'react'; // <-- Возвращаем Suspense
import { Outlet } from 'react-router-dom';
import Header from '../../../widgets/Header/ui/Header';
import Footer from '../../../widgets/Footer/ui/Footer';
import { Registration } from '../../../widgets/Registration/Registration';
import { Login } from '../../../widgets/Login/Login';

// --- ИЗМЕНЕНИЕ 1: Снова импортируем фон ---
// Путь может отличаться, убедитесь, что он правильный
import DynamicSpheres from '../../DarkLayout/ui/DynamicSpheres'; 

import styles from './DarkLayout.module.css';

export const DarkLayout: React.FC = () => {
  const [modalView, setModalView] = useState<'login' | 'register' | null>(null);

  const handleShowLogin = () => setModalView('login');
  const handleShowRegister = () => setModalView('register');
  const handleCloseModal = () => setModalView(null);

  return (
    <div className={styles.layout}>
      {/* --- ИЗМЕНЕНИЕ 2: Возвращаем блок с фоном --- */}
      <div className={styles.backgroundCanvas}>
        <Suspense fallback={null}>
          <DynamicSpheres />
        </Suspense>
      </div>

      <Header onUserIconClick={handleShowLogin} />
      
      <main className={styles.content}>
        <Outlet />
      </main>
      
      <Footer />

      {modalView === 'login' && (
        <Login 
          onClose={handleCloseModal} 
          onShowRegister={handleShowRegister} 
        />
      )}
      
      {modalView === 'register' && (
        <Registration 
          onClose={handleCloseModal} 
          onShowLogin={handleShowLogin} 
        />
      )}
    </div>
  );
};

export default DarkLayout;