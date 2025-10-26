import React, { useState, Suspense } from 'react'; // <-- 1. Добавляем Suspense
import { Outlet } from 'react-router-dom';
import Header from '../../../widgets/Header/ui/Header';
import Footer from '../../../widgets/Footer/ui/Footer';
import { Registration } from '../../../widgets/Registration/Registration';
import { Login } from '../../../widgets/Login/Login';
import DynamicSpheres from '../../MainLayout/ui/DynamicSpheres'; // <-- 2. Импортируем DynamicSpheres
import styles from './MainLayout.module.css';

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

      {/* Ошибка №1 исправлена здесь: передаем prop в Header */}
      <Header onUserIconClick={handleShowLogin} />
      
      <main className={styles.content}>
        <Outlet />
      </main>
      
      <Footer />

      {/* Ошибки №2 и №3 исправлены здесь: передаем нужные props в Login и Registration */}
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