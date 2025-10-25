import React from 'react';
import { FiClock, FiUser } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import styles from './Header.module.css';
const Header: React.FC = () => {
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
        <Link to="/login">
          <FiUser size={20} className={styles.icon} />
        </Link>
      </div>
    </header>
  );
};

export default Header;