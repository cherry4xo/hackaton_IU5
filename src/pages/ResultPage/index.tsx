import React from 'react';
import { useParams } from 'react-router-dom';
import { ResultsDisplay } from '../../widgets/ResultsDisplay/ui';
import styles from '../ResultPage/ResultPage.module.css';

const ResultsPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();

  if (!taskId) {
    return <div className={styles.pageWrapper}>Ошибка: ID задачи не найден в URL.</div>;
  }

  return (
    <div className={styles.pageWrapper}>
      {/* ИСПРАВЛЕНИЕ: Передаем prop с именем `taskId` */}
      <ResultsDisplay taskId={taskId} />
    </div>
  );
};

export default ResultsPage;