// src/widgets/InputResearch/ui/InputResearch.tsx

import React, { useState, useRef, useEffect } from 'react';
import './InputResearch.css';
import { Button } from '../../../shared/ui/Button';

// 1. ТИПЫ ДАННЫХ
interface Observation {
  id: number;
  time: string;
  ra: string;
  dec: string;
}

type FieldErrors = {
  [key: string]: string;
};

// 2. ФУНКЦИЯ-ПОМОЩНИК
const generateInitialRows = (): Observation[] => {
  return Array.from({ length: 5 }, (_, i) => ({
    id: Date.now() + i,
    time: '',
    ra: '',
    dec: '',
  }));
};

// 3. ОСНОВНОЙ КОМПОНЕНТ
export const InputResearch: React.FC = () => {
  // --- СОСТОЯНИЕ КОМПОНЕНТА ---
  const [observations, setObservations] = useState<Observation[]>(generateInitialRows());
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  // ИЗМЕНЕНИЕ №1: Возвращаем состояние для общей ошибки формы
  const [formError, setFormError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ... (useEffect без изменений)
  useEffect(() => {
    return () => { previews.forEach(url => URL.revokeObjectURL(url)); };
  }, [previews]);

  // --- ОБРАБОТЧИКИ СОБЫТИЙ ---
  const handleAddRow = () => {
    setObservations(prev => [...prev, { id: Date.now(), time: '', ra: '', dec: '' }]);
  };

  const handleDeleteRow = (id: number) => {
    if (observations.length > 1) {
      setObservations(prev => prev.filter(obs => obs.id !== id));
    }
  };

  const handleInputChange = (id: number, field: keyof Omit<Observation, 'id'>, value: string) => {
    setFormError(null); // Сбрасываем общую ошибку при любом вводе
    const errorKey = `${id}-${field}`;
    if (fieldErrors[errorKey]) {
      const newErrors = { ...fieldErrors };
      delete newErrors[errorKey];
      setFieldErrors(newErrors);
    }
    setObservations(prev =>
      prev.map(obs => (obs.id === id ? { ...obs, [field]: value } : obs))
    );
  };

const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const newFiles = Array.from(event.target.files);
      // Создаем URL-превью из новых файлов
      const newPreviews = newFiles.map(file => URL.createObjectURL(file));
      
      // Добавляем ТОЛЬКО файлы в состояние `files`
      setFiles(prev => [...prev, ...newFiles]);
      // Добавляем ТОЛЬКО URL-строки в состояние `previews`
      setPreviews(prev => [...prev, ...newPreviews]);
    }
};
  
  // ИЗМЕНЕНИЕ №2: ОБНОВЛЕННАЯ ФУНКЦИЯ ВАЛИДАЦИИ
  const handleCalculate = async () => {
    // --- ПРОВЕРКА №1: Минимальное количество строк ---
    if (observations.length < 5) {
      setFormError('Необходимо как минимум 5 строк наблюдений.');
      setFieldErrors({}); // Сбрасываем ошибки полей, если они были
      return;
    }

    // --- ПРОВЕРКА №2: Заполнение и формат полей ---
    const newErrors: FieldErrors = {};
    let hasError = false;

    observations.forEach(obs => {
      if (!obs.time) { newErrors[`${obs.id}-time`] = 'Заполните'; hasError = true; }
      if (!obs.ra.trim()) { newErrors[`${obs.id}-ra`] = 'Заполните'; hasError = true; }
      else if (isNaN(parseFloat(obs.ra))) { newErrors[`${obs.id}-ra`] = 'Неверный формат'; hasError = true; }
      if (!obs.dec.trim()) { newErrors[`${obs.id}-dec`] = 'Заполните'; hasError = true; }
      else if (isNaN(parseFloat(obs.dec))) { newErrors[`${obs.id}-dec`] = 'Неверный формат'; hasError = true; }
    });

    setFieldErrors(newErrors);

    if (hasError) {
      setFormError(null); // Убираем общую ошибку, т.к. показываем ошибки полей
      return;
    }
    
    // --- ОТПРАВКА ДАННЫХ, ЕСЛИ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ ---
    setFormError(null);
    setFieldErrors({});
    setIsLoading(true);

    const formData = new FormData();
    const observationsData = observations.map(({ id, ...rest }) => rest);
    formData.append('observations', JSON.stringify(observationsData));
    files.forEach((file, index) => { formData.append(`file${index}`, file); });

    console.log("Отправка данных на бэкенд...");
    try {
      const response = await fetch('https://your-backend-api.com/calculate', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Ошибка на сервере');
      }
      const result = await response.json();
      console.log('Ответ от бэкенда:', result);
    } catch (error) {
      console.error('Ошибка при отправке:', error);
      if (error instanceof Error) {
        setFormError(`Ошибка: ${error.message}`);
      } else {
        setFormError('Произошла неизвестная ошибка.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // --- РЕНДЕРИНГ КОМПОНЕНТА (JSX) ---
  return (
    <div className="research-container">
      <h2 className="research-title">Расчёт</h2>
      <div className="content-wrapper">
        <div className="input-section">
          {/* ... (разметка до кнопок) ... */}
          <div className="observations-header">
            <span>Время наблюдения</span>
            <span>Прямое восхождение</span>
            <span>Склонение</span>
          </div>
          <div className="observations-list">
            {observations.map((obs, index) => {
              const timeError = fieldErrors[`${obs.id}-time`];
              const raError = fieldErrors[`${obs.id}-ra`];
              const decError = fieldErrors[`${obs.id}-dec`];

              return (
                <div key={obs.id} className="observation-row">
                  <span className="row-number">{index + 1}</span>
                  <div className="input-wrapper datetime-wrapper">
                    <input
                      type="datetime-local"
                      step="1"
                      required
                      value={obs.time}
                      onChange={(e) => handleInputChange(obs.id, 'time', e.target.value)}
                      className={`obs-input ${timeError ? 'input-error' : ''}`}
                    />
                    {timeError && <span className="field-error-message">{timeError}</span>}
                  </div>
                  <div className="input-wrapper">
                    <input
                      type="number"
                      step="any"
                      placeholder="..."
                      value={obs.ra}
                      onChange={(e) => handleInputChange(obs.id, 'ra', e.target.value)}
                      className={`obs-input ${raError ? 'input-error' : ''}`}
                    />
                    {raError && <span className="field-error-message">{raError}</span>}
                  </div>
                  <div className="input-wrapper">
                    <input
                      type="number"
                      step="any"
                      placeholder="..."
                      value={obs.dec}
                      onChange={(e) => handleInputChange(obs.id, 'dec', e.target.value)}
                      className={`obs-input ${decError ? 'input-error' : ''}`}
                    />
                    {decError && <span className="field-error-message">{decError}</span>}
                  </div>
                  <button onClick={() => handleDeleteRow(obs.id)} className="delete-row-button" disabled={observations.length <= 1}>-</button>
                </div>
              );
            })}
          </div>
          <button onClick={handleAddRow} className="add-row-button">Добавить строку</button>
        </div>
        <div className="file-upload-section">
          <input
            type="file"
            multiple
            accept="image/*,.fits,.fit"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          {previews.length > 0 ? (
            <div className="image-preview-container">
              {previews.map((src, index) => (
                <img key={index} src={src} alt={`preview ${index}`} className="image-preview" />
              ))}
            </div>
          ) : (
            <div className="file-drop-zone" onClick={() => fileInputRef.current?.click()}>
              <span className="upload-icon"><svg width="61" height="60" viewBox="0 0 61 60" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M30.4997 12.5V47.5M12.708 30H48.2913" stroke="#B3B3B3" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
</span>
              <span className="upload-text">Загрузите медиафайлы</span>
            </div>
          )}
        </div>
      </div>
      
      {/* ИЗМЕНЕНИЕ №3: Возвращаем отображение общей ошибки формы */}
      {formError && (
        <div className="form-error-message">
          {formError}
        </div>
      )}

      <Button 
        size="lg" 
        className="calculate-button" 
        onClick={handleCalculate}
        disabled={isLoading}
        loading={isLoading}
      >
        {isLoading ? 'Расчёт...' : 'Рассчитать координаты'}
      </Button>
    </div>
  );
};