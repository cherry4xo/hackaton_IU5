import React from 'react';
import { Breadcrumbs } from '../../../shared/ui/Breadcrumbs';
import { ObservationCarousel } from './ObservationCarousel';
import styles from './UserProfile.module.css';

interface UserData {
  name: string;
  email: string;
  login: string;
  avatar?: string;
}

export const UserProfile: React.FC = () => {
  // Временные данные, потом заменим на данные из контекста/бэкенда
  const userData: UserData = {
    name: "Темный принц",
    email: "draft@gmail.com",
    login: "terminprinc20"
  };

  const breadcrumbs = [
    { label: 'Пользователь', path: '/profile' },
    { label: 'Мой профиль', path: '/profile' }
  ];

  return (
    <div className={styles.profilePage}>
      {/* Хлебные крошки */}
      <div className={styles.breadcrumbsContainer}>
        <Breadcrumbs items={breadcrumbs} />
      </div>

      {/* Основной контент */}
      <div className={styles.profileContent}>
        {/* Левая колонка - информация о пользователе */}
        <div className={styles.userInfoSection}>
          <div className={styles.avatarContainer}>
            <div className={styles.avatar}>
              {userData.avatar ? (
                <img src={userData.avatar} alt="Аватар" />
              ) : (
                <div className={styles.avatarPlaceholder}>
                  <svg width="60" height="60" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </div>
              )}
            </div>
          </div>

          <h1 className={styles.userName}>{userData.name}</h1>
          <div className={styles.userCredentials}>
            <span className={styles.email}>{userData.email}</span>
            <span className={styles.separator}>×</span>
            <span className={styles.login}>{userData.login}</span>
          </div>
        </div>

        {/* Правая колонка - наблюдения */}
        <div className={styles.observationsSection}>
          <h2 className={styles.observationsTitle}>Мои наблюдения</h2>
          <ObservationCarousel />
        </div>
      </div>

      {/* Кнопка настроек */}
      <div className={styles.settingsSection}>
        <button className={styles.settingsButton} disabled>
          Настройки
        </button>
      </div>
    </div>
  );
};