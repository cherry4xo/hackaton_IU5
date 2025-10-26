import React from 'react';
import { ResultsDisplay } from '../../widgets/ResultsDisplay/ui';
import styles from './ResultsPage.module.css';

const ResultsPage: React.FC = () => {
  return (
    <div className={styles.pageWrapper}>
      <ResultsDisplay />
    </div>
  );
};

export default ResultsPage;