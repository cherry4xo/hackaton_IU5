import React from 'react';
import HistoryTimelineWidget  from "../../widgets/HistoryPage/ui/HistoryPage"
// import { HistoryPage } from '../../widgets/HistoryPage/ui/HistoryPage';
import styles from './HistortyPage.module.css';

const HistoryPage: React.FC = () => {
  return (
    <div className={styles.pageWrapper}>
        <HistoryTimelineWidget  />
    </div>
  );
};

export default HistoryPage;