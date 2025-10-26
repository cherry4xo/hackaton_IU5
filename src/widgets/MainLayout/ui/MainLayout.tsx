import React, { useState, Suspense } from 'react'; // <-- 1. Добавляем Suspense
import { Outlet } from 'react-router-dom';
import Header from '../../../widgets/Header/ui/Header';
import Footer from '../../../widgets/Footer/ui/Footer';
import { Registration } from '../../../widgets/Registration/Registration';
import { Login } from '../../../widgets/Login/Login';
import DynamicSpheres from '../../MainLayout/ui/DynamicSpheres'; // <-- 2. Импортируем DynamicSpheres
import styles from './MainLayout.module.css';

// 2. УБИРАЕМ `children` из props
export const MainLayout: React.FC = () => {
  const [modalView, setModalView] = useState<'login' | 'register' | null>(null);

  const handleShowLogin = () => setModalView('login');
  const handleShowRegister = () => setModalView('register');
  const handleCloseModal = () => setModalView(null);

  return (
    <div className={styles.layout}>
      <div className={styles.backgroundCanvas}>
        <Suspense fallback={null}>
          <DynamicSpheres />
        </Suspense>
      </div>

      <Header onUserIconClick={handleShowLogin} />
      
      <main className={styles.content}>
        {/* 3. ИСПОЛЬЗУЕМ <Outlet /> ЗДЕСЬ */}
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