// src/widgets/Header/ui/Header.tsx

import React from 'react';
import { FiClock, FiUser, FiLogOut } from 'react-icons/fi';
import { Link } from 'react-router-dom';
import styles from './Header.module.css';
import { useAuth } from '../../../app/providers/AuthProvider'; 

interface HeaderProps {
  onUserIconClick: () => void; // Функция для открытия модального окна входа
}

const Header: React.FC<HeaderProps> = ({ onUserIconClick }) => {
  // Получаем данные о пользователе, статус загрузки и функцию выхода из глобального контекста
  const { user, logout, isLoading } = useAuth();

  return (
    <header className={styles.header}>
      {/* Ссылка на главную страницу */}
      <Link to="/" className={styles.logoLink}>
        <div className={styles.logo}>
          cometrak 2.0
        </div>
      </Link>

      {/* Навигационное меню */}
      <nav className={styles.navigation}>
        <Link to="/calculate" className={styles.navLink}>Расчет</Link>
        <Link to="/library" className={styles.navLink}>Библиотека астрономических тел</Link>
        <Link to="/projects" className={styles.navLink}>Проекты</Link>
      </nav>
      
      {/* Иконки действий пользователя */}
      <div className={styles.userActions}>
        <FiClock size={20} className={styles.icon} />
        
        {/* 
          Условный рендеринг:
          - Не показываем ничего, пока идет проверка авторизации (isLoading).
          - Если пользователь есть (авторизован), показываем его имя и кнопку "Выйти".
          - Если пользователя нет, показываем кнопку "Войти".
        */}
        {!isLoading && (
          user ? (
            <>
              <span className={styles.username}>{user.username}</span>
              <button onClick={logout} className={styles.iconButton} title="Выйти">
                <FiLogOut size={20} />
              </button>
            </>
          ) : (
            <button onClick={onUserIconClick} className={styles.iconButton} title="Войти">
                <FiUser size={20} />
            </button>
          )
        )}
      </div>
    </header>
  );
};

export default Header;