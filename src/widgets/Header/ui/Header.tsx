import React from 'react';
import { FiClock, FiUser, FiLogOut } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import styles from './Header.module.css';
import { useAuth } from '../../../app/providers/AuthProvider'; 

const Header: React.FC = () => {
  const { user, logout, isLoading } = useAuth();

  return (
    <header className={styles.header}>
      <Link to="/" className={styles.logoLink}>
        <div className={styles.logo}>
          cometrak 2.0
        </div>
      </Link>

      <nav className={styles.navigation}>
        <Link to="/" className={styles.navLink}>Расчет</Link>
        <Link to="/library" className={styles.navLink}>Библиотека астрономических тел</Link>
        <Link to="/projects" className={styles.navLink}>Проекты</Link>
      </nav>
      
      <div className={styles.userActions}>
        <Link to="/history" className={styles.iconLink} title="История наблюдений">
          <FiClock size={20} />
        </Link>
        
        {!isLoading && (
          user ? (
            <>
              {/* ЗАМЕНИЛИ кнопку на ссылку на профиль */}
              <Link to="/profile" className={styles.username} title="Мой профиль">
                {user.username}
              </Link>
              <button onClick={logout} className={styles.iconButton} title="Выйти">
                <FiLogOut size={20} />
              </button>
            </>
          ) : (
            /* ЗАМЕНИЛИ кнопку на ссылку на страницу входа/регистрации */
            <Link to="/login" className={styles.iconButton} title="Войти">
              <FiUser size={20} />
            </Link>
          )
        )}
      </div>
    </header>
  );
};

export default Header;  