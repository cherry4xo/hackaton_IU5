// src/widgets/ResultsDisplay/ui/index.tsx


import React, { useState, useEffect } from 'react';
import { Button } from '../../../shared/ui/Button';
import { calculateClosestApproach, getTaskResult } from '../../../shared/api/calculate';
import styles from './ResultsDisplay.module.css';

// 1. ТИПЫ ДАННЫХ
interface OrbitalParams {
    uuid: string; 
  a: number; ecc: number; inc: number; raan: number; argp: number; nu: number;
}
interface CloseApproachResult {
  time: string; distance_au: number; distance_km: number;
}
interface ResultsDisplayProps {
  taskId: string;
}

// 2. ОСНОВНОЙ КОМПОНЕНТ
export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ taskId }) => {
  // --- СОСТОЯНИЕ КОМПОНЕНТА ---
  const [orbitalParams, setOrbitalParams] = useState<OrbitalParams | null>(null);
  const [taskStatus, setTaskStatus] = useState<string>('PENDING');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [timeError, setTimeError] = useState<string | null>(null);
  const [approachResult, setApproachResult] = useState<CloseApproachResult | null>(null);
  const [isCalculatingApproach, setIsLoadingApproach] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const paramsConfig = [
    { key: 'a' as keyof OrbitalParams, label: 'Большая полуось', unit: 'AU' },
    { key: 'ecc' as keyof OrbitalParams, label: 'Эксцентриситет', unit: '' },
    { key: 'inc' as keyof OrbitalParams, label: 'Наклонение', unit: 'град' },
    { key: 'raan' as keyof OrbitalParams, label: 'Долгота восходящего узла', unit: 'град' },
    { key: 'argp' as keyof OrbitalParams, label: 'Аргумент перицентра', unit: 'град' },
    { key: 'nu' as keyof OrbitalParams, label: 'Истинная аномалия', unit: 'град' }
  ];

  // --- ФИНАЛЬНЫЙ ИСПРАВЛЕННЫЙ useEffect ДЛЯ ОПРОСА СТАТУСА ---
  useEffect(() => {
    // Этот флаг предотвращает обновление состояния, если компонент уже размонтирован
    let isMounted = true; 

    const pollTask = async () => {
      // Если компонент размонтирован, прекращаем все действия
      if (!isMounted) return;

      try {
        const result = await getTaskResult(taskId);
        if (!isMounted) return;

        console.log('Проверка статуса:', result.status);

        // Используем статусы из вашей документации
        if (result.status === 'SUCCESS') {
          setTaskStatus('SUCCESS');
          const orbitResult = result.result.orbit_result;
          setOrbitalParams({
            uuid: orbitResult.uuid, 
              a: orbitResult.semi_major_axis,
              ecc: orbitResult.eccentricity,
              inc: orbitResult.inclination,
              raan: orbitResult.longitude_ascending_node,
              argp: orbitResult.argument_periapsis,
              nu: orbitResult.true_anomaly || 0
          });
          // Статус финальный, опрос прекращается. Мы не вызываем setTimeout.
        } else if (result.status === 'FAILURE') {
          setApiError(result.result?.error || 'Расчет орбиты не удался');
          setTaskStatus('FAILURE');
          // Статус финальный, опрос прекращается.
        } else {
          // Если статус PENDING или STARTED, планируем следующий вызов через 3 секунды
          setTimeout(pollTask, 3000);
        }
      } catch (error: any) {
        if (isMounted) {
          setApiError(error.message || 'Ошибка при получении результатов');
          setTaskStatus('FAILURE');
        }
      }
    };

    // Запускаем опрос только один раз при монтировании
    pollTask();

    // Функция очистки: React вызовет ее, когда вы уйдете со страницы
    return () => {
      isMounted = false;
    };
  }, [taskId]); // Эффект зависит ТОЛЬКО от taskId

  // --- ОБРАБОТЧИКИ СОБЫТИЙ ---
  const handleStartTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setStartTime(e.target.value);
    if (timeError || apiError) { setTimeError(null); setApiError(null); }
  };
  const handleEndTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEndTime(e.target.value);
    if (timeError || apiError) { setTimeError(null); setApiError(null); }
  };
  const handleCalculateApproach = async () => {
    // 1. Валидация времени на клиенте
    if (!startTime || !endTime) {
      setTimeError('Заполните оба поля времени');
      return;
    }
    if (new Date(startTime) >= new Date(endTime)) {
      setTimeError('Конечное время должно быть позже начального');
      return;
    }

    // Сбрасываем ошибки и включаем загрузку
    setTimeError(null);
    setApiError(null);
    setIsLoadingApproach(true);
    
    try {
      // 2. Проверяем, что ID орбиты уже загружен
      if (!orbitalParams?.uuid) {
        // Эта ошибка появится, если пользователь нажмет кнопку до того,
        // как завершится основной расчет.
        throw new Error("ID орбиты еще не получен. Пожалуйста, подождите.");
      }

      // 3. Отправляем запрос на бэкенд со всеми необходимыми данными
      const result = await calculateClosestApproach({
        orbit_id: orbitalParams.uuid,
        observation_start_time: startTime,
        observation_end_time: endTime,
      });
      
      console.log('Расчет сближения запущен! Ответ:', result);
      alert(`Задача на расчет сближения отправлена! ID: ${result.task_id}`);
      // В будущем здесь можно будет запустить опрос статуса для этой новой задачи

    } catch (error: any) {
      console.error('Ошибка при расчете сближения:', error);
      setApiError(error.detail?.[0]?.msg || error.message || 'Произошла ошибка');
    } finally {
      setIsLoadingApproach(false);
    }
  };

  const formatDateTime = (datetime: string) => {
    const date = new Date(datetime);
    return date.toLocaleString('ru-RU', { timeZone: 'UTC', /* ... */ });
  };

  // --- РЕНДЕРИНГ КОМПОНЕНТА (JSX) ---
  if (taskStatus === 'PENDING' || taskStatus === 'STARTED') {
    return <div className={styles.statusMessage}>Идет расчет орбиты, пожалуйста, подождите...</div>;
  }
  if (taskStatus === 'FAILURE') {
    return <div className={styles.statusMessageError}>Ошибка: {apiError}</div>;
  }
  if (!orbitalParams) {
    return <div className={styles.statusMessageError}>Не удалось загрузить параметры орбиты.</div>;
  }

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
          loading={isCalculatingApproach}
          disabled={isCalculatingApproach}
        >
          {isCalculatingApproach ? 'Расчёт сближения...' : 'Рассчитать сближение'}
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