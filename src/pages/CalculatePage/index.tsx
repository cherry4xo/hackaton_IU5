import React from 'react';
import { InputResearch } from '../../widgets/InputResearch/ui/InputResearch';
import styles from './CalculatePage.module.css';

const CalculatePage: React.FC = () => {
  return (
    <div className={styles.pageWrapper}> 
      <InputResearch />
    </div>
  );
};

export default CalculatePage;