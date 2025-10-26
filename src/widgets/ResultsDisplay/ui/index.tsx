// src/widgets/ResultsDisplay/ui/index.tsx

import React, { useState } from 'react';
import { Button } from '../../../shared/ui/Button';
import { calculateClosestApproach } from '../../../shared/api/calculate';
import styles from './ResultsDisplay.module.css';

// 1. ТИПЫ ДАННЫХ
interface OrbitalParams {
  a: number; ecc: number; inc: number; raan: number; argp: number; nu: number;
}
interface CloseApproachResult {
  time: string; distance_au: number; distance_km: number;
}

// 2. ИНТЕРФЕЙС ДЛЯ PROPS
interface ResultsDisplayProps {
  orbitId: string;
}

// 3. ОСНОВНОЙ КОМПОНЕНТ
export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ orbitId }) => {
  // --- СОСТОЯНИЕ КОМПОНЕНТА ---
  const [orbitalParams, setOrbitalParams] = useState<OrbitalParams>({
    a: 100, ecc: 100, inc: 100, raan: 100, argp: 100, nu: 100
  });
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [timeError, setTimeError] = useState<string | null>(null);
  const [approachResult, setApproachResult] = useState<CloseApproachResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const paramsConfig = [
    { key: 'a' as keyof OrbitalParams, label: 'Большая полуось', unit: 'AU' },
    { key: 'ecc' as keyof OrbitalParams, label: 'Эксцентриситет', unit: '' },
    { key: 'inc' as keyof OrbitalParams, label: 'Наклонение', unit: 'град' },
    { key: 'raan' as keyof OrbitalParams, label: 'Долгота восходящего узла', unit: 'град' },
    { key: 'argp' as keyof OrbitalParams, label: 'Аргумент перицентра', unit: 'град' },
    { key: 'nu' as keyof OrbitalParams, label: 'Истинная аномалия', unit: 'град' }
  ];

  // --- ОБРАБОТЧИКИ СОБЫТИЙ ---
  const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setStartTime(e.target.value);
    if (timeError || apiError) { setTimeError(null); setApiError(null); }
  };
  const handleEndTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEndTime(e.target.value);
    if (timeError || apiError) { setTimeError(null); setApiError(null); }
  };

  // --- ФИНАЛЬНАЯ ФУНКЦИЯ РАСЧЕТА СБЛИЖЕНИЯ ---
  const handleCalculateApproach = async () => {
    if (!startTime || !endTime) { setTimeError('Заполните оба поля времени'); return; }
    if (new Date(startTime) >= new Date(endTime)) { setTimeError('Конечное время должно быть позже начального'); return; }

    setTimeError(null);
    setApiError(null);
    setIsLoading(true);
    
    try {
      // Отправляем реальный запрос на бэкенд с ID орбиты
      const result = await calculateClosestApproach({ orbit_id: orbitId });
      
      console.log('Расчет сближения запущен! Ответ от бэкенда:', result);
      
      // ВАЖНО: Это асинхронная задача. Бэкенд возвращает `task_id`.
      // Чтобы получить РЕЗУЛЬТАТ, нужно будет создать еще один эндпоинт 
      // и периодически опрашивать его с этим `task_id`.
      // Пока что мы просто покажем alert, что задача запущена.
      alert(`Задача на расчет сближения отправлена! ID задачи: ${result.task_id}`);

    } catch (error: any) {
      console.error('Ошибка при расчете сближения:', error);
      setApiError(error.detail || error.message || 'Произошла ошибка при расчете сближения');
    } finally {
      setIsLoading(false);
    }
  };

  // Функция для форматирования даты
  const formatDateTime = (datetime: string) => {
    const date = new Date(datetime);
    return date.toLocaleString('ru-RU', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  };

  // --- РЕНДЕРИНГ КОМПОНЕНТА (JSX) ---
  return (
    <div className={styles.resultsContainer}>
      <h2 className={styles.researchTitle}>Результаты Расчёта</h2>
      
      <div className={styles.resultsContent}>
        <div className={styles.resultsHeader}>
          <span>Измерение</span>
          <span>Результат</span>
          <span>Ед. измерения</span>
        </div>
        <div className={styles.resultsList}>
          {paramsConfig.map((param) => (
            <div key={param.key} className={styles.resultRow}>
              <span className={styles.paramLabel}>{param.label}</span>
              <span className={styles.paramValue}>{orbitalParams[param.key]}</span>
              <span className={styles.paramUnit}>{param.unit}</span>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.searchRangeSection}>
        <h3 className={styles.searchRangeTitle}>Диапазон поиска сближения с Землёй</h3>
        
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

        {timeError && <div className={styles.timeError}>{timeError}</div>}
        {apiError && <div className={styles.timeError}>{apiError}</div>}

        <Button 
          size="lg" 
          className={styles.calculateApproachButton}
          onClick={handleCalculateApproach}
          loading={isLoading}
          disabled={isLoading}
        >
          {isLoading ? 'Расчёт сближения...' : 'Рассчитать сближение'}
        </Button>

        {approachResult && (
          <div className={styles.approachResultSection}>
            <h3 className={styles.approachResultTitle}>Ближайшее сближение</h3>
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