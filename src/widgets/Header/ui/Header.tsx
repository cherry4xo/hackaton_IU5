// src/widgets/Header/ui/Header.tsx

import React from 'react';
import { FiClock, FiUser } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import styles from './Header.module.css';

// 1. Интерфейс для props (здесь все было правильно)
interface HeaderProps {
  onUserIconClick: () => void;
}

// 2. ИСПРАВЛЕНИЕ: Используем правильное имя переменной без дефиса
const Header: React.FC<HeaderProps> = ({ onUserIconClick }) => {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        cometrak 2.0
      </div>
      <nav className={styles.navigation}>
        <Link to="/calculate" className={styles.navLink}>Расчет</Link>
        <Link to="/library" className={styles.navLink}>Библиотека астрономических тел</Link>
      </nav>
      <div className={styles.userActions}>
        <FiClock size={20} className={styles.icon} />
        <button onClick={onUserIconClick} className={styles.iconButton}>
          <FiUser size={20} />
        </button>
      </div>
    </header>
  );
};

export default Header;