import React, { useState } from 'react';
import { Button } from '../../../shared/ui/Button';
import styles from './ResultsDisplay.module.css';

interface OrbitalParams {
  a: number;      // большая полуось, AU
  ecc: number;    // эксцентриситет
  inc: number;    // наклонение (град)
  raan: number;   // долгота восходящего узла
  argp: number;   // аргумент перицентра  
  nu: number;     // истинная аномалия
}

interface CloseApproachResult {
  time: string;        // datetime
  distance_au: number; // дистанция в AU
  distance_km: number; // дистанция в км
}

export const ResultsDisplay: React.FC = () => {
  // Пока используем константы, потом заменим на данные с бэкенда
  const orbitalParams: OrbitalParams = {
    a: 100,
    ecc: 100, 
    inc: 100,
    raan: 100,
    argp: 100,
    nu: 100
  };

  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [timeError, setTimeError] = useState<string | null>(null);
  const [approachResult, setApproachResult] = useState<CloseApproachResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const paramsConfig = [
    { key: 'a' as keyof OrbitalParams, label: 'Большая полуось', unit: 'AU' },
    { key: 'ecc' as keyof OrbitalParams, label: 'Эксцентриситет', unit: '' },
    { key: 'inc' as keyof OrbitalParams, label: 'Наклонение', unit: 'град' },
    { key: 'raan' as keyof OrbitalParams, label: 'Долгота восходящего узла', unit: 'град' },
    { key: 'argp' as keyof OrbitalParams, label: 'Аргумент перицентра', unit: 'град' },
    { key: 'nu' as keyof OrbitalParams, label: 'Истинная аномалия', unit: 'град' }
  ];

  const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setStartTime(e.target.value);
    if (timeError) setTimeError(null);
  };

  const handleEndTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEndTime(e.target.value);
    if (timeError) setTimeError(null);
  };

  const handleCalculateApproach = async () => {
    // Валидация времени
    if (!startTime || !endTime) {
      setTimeError('Заполните оба поля времени');
      return;
    }

    if (new Date(startTime) >= new Date(endTime)) {
      setTimeError('Конечное время должно быть позже начального');
      return;
    }

    setTimeError(null);
    setIsLoading(true);
    
    console.log("Начальное время:", startTime);
    console.log("Конечное время:", endTime);
    console.log("Орбитальные параметры:", orbitalParams);
    
    // Имитация API запроса
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Пока используем константы, потом заменим на реальные данные с бэкенда
      const mockResult: CloseApproachResult = {
        time: "2024-12-15T14:30:00",
        distance_au: 0.025,
        distance_km: 3740000
      };
      
      setApproachResult(mockResult);
    } catch (error) {
      console.error('Ошибка при расчете:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDateTime = (datetime: string) => {
    const date = new Date(datetime);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className={styles.resultsContainer}>
      <h2 className={styles.researchTitle}>Расчёт</h2>
      
      {/* Секция с орбитальными параметрами */}
      <div className={styles.resultsContent}>
        <div className={styles.resultsHeader}>
          <span>Измерение</span>
          <span>Результат</span>
          <span>Ед. измерения</span>
        </div>

        <div className={styles.resultsList}>
          {paramsConfig.map((param, index) => (
            <div key={param.key} className={styles.resultRow}>
              <span className={styles.paramLabel}>{param.label}</span>
              <span className={styles.paramValue}>{orbitalParams[param.key]}</span>
              <span className={styles.paramUnit}>{param.unit}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Секция диапазона поиска */}
      <div className={styles.searchRangeSection}>
        <h3 className={styles.searchRangeTitle}>Диапазон поиска</h3>
        
        <div className={styles.timeInputsContainer}>
          <div className={styles.timeInputGroup}>
            <label className={styles.timeLabel}>Начальное время</label>
            <div className={styles.inputWrapper}>
              <input
                type="datetime-local"
                step="1"
                value={startTime}
                onChange={handleStartTimeChange}
                className={`${styles.timeInput} ${timeError ? styles.inputError : ''}`}
              />
            </div>
          </div>
          
          <div className={styles.timeInputGroup}>
            <label className={styles.timeLabel}>Конечное время</label>
            <div className={styles.inputWrapper}>
              <input
                type="datetime-local"
                step="1"
                value={endTime}
                onChange={handleEndTimeChange}
                className={`${styles.timeInput} ${timeError ? styles.inputError : ''}`}
              />
            </div>
          </div>
        </div>

        {/* Отображение ошибки времени */}
        {timeError && (
          <div className={styles.timeError}>
            {timeError}
          </div>
        )}

        <Button 
          size="lg" 
          className={styles.calculateApproachButton}
          onClick={handleCalculateApproach}
          loading={isLoading}
          disabled={isLoading}
        >
          {isLoading ? 'Расчёт сближения...' : 'Рассчитать сближение с Землёй'}
        </Button>

        {/* Блок результатов сближения */}
        {approachResult && (
          <div className={styles.approachResultSection}>
            <h3 className={styles.approachResultTitle}>Ближайшее сближение кометы с Землёй</h3>
            
            <div className={styles.approachResultsList}>
              <div className={styles.approachResultRow}>
                <span className={styles.approachParamLabel}>Время сближения</span>
                <span className={styles.approachParamValue}>
                  {formatDateTime(approachResult.time)}
                </span>
              </div>
              
              <div className={styles.approachResultRow}>
                <span className={styles.approachParamLabel}>Дистанция</span>
                <span className={styles.approachParamValue}>
                  {approachResult.distance_au.toFixed(6)} AU
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};