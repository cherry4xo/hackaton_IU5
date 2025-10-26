import React from 'react';
import styles from './ObservationCarousel.module.css';

interface Observation {
  id: number;
  name: string;
  image: string;
}

export const ObservationCarousel: React.FC = () => {
  // Временные данные наблюдений
  const observations: Observation[] = Array.from({ length: 5 }, (_, i) => ({
    id: i + 1,
    name: 'Булочка',
    image: '/src/assets/comet-default.jpg' // Замени на путь к твоей картинке
  }));

  return (
    <div className={styles.carouselContainer}>
      <div className={styles.carousel}>
        {observations.map((observation) => (
          <div key={observation.id} className={styles.observationCard}>
            <div className={styles.cardImage}>
              <img 
                src={observation.image} 
                alt={observation.name}
                onError={(e) => {
                  // Fallback если картинка не загрузится
                  e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDIwMCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMTUwIiBmaWxsPSIjMUEwMEE2Ii8+CjxwYXRoIGQ9Ik0xMDAgNzVDMTA3LjcgNzUgMTE0IDY4LjcgMTE0IDYxQzExNCA1My4zIDEwNy43IDQ3IDEwMCA0N0M5Mi4zIDQ3IDg2IDUzLjMgODYgNjFDODYgNjguNyA5Mi4zIDc1IDEwMCA3NVoiIGZpbGw9IiM1QzQ5RkYiLz4KPHBhdGggZD0iTTc1IDEwMkM3NSAxMDIgODAgMTE1IDEwMCAxMTVDMTIwIDExNSAxMjUgMTAyIDEyNSAxMDJDMTI1IDEwMiAxMTUgMTE1IDEwMCAxMTVDODUgMTE1IDc1IDEwMiA3NSAxMDJaIiBmaWxsPSIjNUM0OUZGIi8+Cjwvc3ZnPgo=';
                }}
              />
            </div>
            <div className={styles.cardContent}>
              <h3 className={styles.cometName}>{observation.name}</h3>
              <button className={styles.viewButton} disabled>
                Просмотреть
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};