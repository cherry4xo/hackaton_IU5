import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styles from './Header.module.css';

export const Header: React.FC = () => {
  const location = useLocation();

  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <Link to="/">cometrack 2.0</Link>
      </div>
      
      <nav className={styles.nav}>
        <Link 
          to="/" 
          className={`${styles.navLink} ${location.pathname === '/' ? styles.active : ''}`}
        >
          Расчет
        </Link>
        <Link 
          to="/library" 
          className={`${styles.navLink} ${location.pathname === '/library' ? styles.active : ''}`}
        >
          Библиотека
        </Link>
        <Link 
          to="/projects" 
          className={`${styles.navLink} ${location.pathname === '/projects' ? styles.active : ''}`}
        >
          Проекты
        </Link>
      </nav>

      <div className={styles.userSection}>
        <Link to="/profile" className={styles.userIcon}>
          {/* Иконка пользователя */}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
        </Link>
      </div>
    </header>
  );
};