import React, { Suspense } from 'react';
import styles from './HeroSection.module.css';
import DynamicSpheres from '../../MainLayout/ui/DynamicSpheres';
import { Button } from '../../../shared/ui/Button';

const HeroSection: React.FC = () => {
  return (
    <div className={styles.hero}>
      <div className={styles.content}>
        <h1 className={styles.title}>cometrak 2.0</h1>
        <p className={styles.description}>
          Платформа Cometrak 2.0 позволит вам
          получить точный прогноз столкновения на
          основе актуальных данных. Введите параметры
          известного небесного тела или выберите объект
          из нашей обновляемой библиотеки, чтобы
          запустить симуляцию и увидеть результат на
          интерактивной карте мира.
        </p>
        <Button variant="outline" size="lg" className={styles.heroButton}>
          Получить прогноз
        </Button>
      </div>
    </div>
  );
};

export default HeroSection;
