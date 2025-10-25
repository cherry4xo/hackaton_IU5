import React from 'react';
import { FiClock, FiUser } from 'react-icons/fi';
import styles from './Header.module.css';

const Header: React.FC = () => {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        cometrak 2.0
      </div>
      <nav className={styles.navigation}>
        <a href="#calculate">Расчет</a>
        <a href="#library">Библиотека астрономических тел</a>
      </nav>
      <div className={styles.userActions}>
        <FiClock size={20} className={styles.icon} />
        <FiUser size={20} className={styles.icon} />
      </div>
    </header>
  );
};

export default Header;