import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../../../widgets/Header/ui/Header';
import Footer from '../../../widgets/Footer/ui/Footer';
import styles from './MainLayout.module.css';

export const MainLayout: React.FC = () => {
  return (
    <div className={styles.layout}>
      <Header />
      <main className={styles.content}>
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};