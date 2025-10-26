import React from 'react';
import { useParams } from 'react-router-dom';
import { ResultsDisplay } from '../../widgets/ResultsDisplay/ui';
import styles from './ResultsPage.module.css';

const ResultsPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();

  // Если по какой-то причине taskId отсутствует, можно показать заглушку
  if (!taskId) {
    return <div className={styles.pageWrapper}>Ошибка: ID задачи не найден.</div>;
  }

  return (
    <div className={styles.pageWrapper}>
      {/* Передаем ID в компонент ResultsDisplay */}
      <ResultsDisplay orbitId={taskId} />
    </div>
  );
};

export default ResultsPage;