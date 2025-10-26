// src/widgets/InputResearch/ui/InputResearch.tsx

import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './InputResearch.css';
import { Button } from '../../../shared/ui/Button';
import { Input } from '../../../shared/ui/Input';
import { calculateOrbit } from '../../../shared/api/calculate';

// 1. ТИПЫ ДАННЫХ
interface Observation {
  id: number;
  time: string;
  ra: string;
  dec: string;
}
type FieldErrors = { [key: string]: string; };

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
  const navigate = useNavigate();
  
  // --- СОСТОЯНИЕ КОМПОНЕНТА ---
  const [observations, setObservations] = useState<Observation[]>(generateInitialRows());
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [cometName, setCometName] = useState<string>('');
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    setFormError(null);
    const errorKey = `${id}-${field}`;
    if (fieldErrors[errorKey]) {
      const newErrors = { ...fieldErrors };
      delete newErrors[errorKey];
      setFieldErrors(newErrors);
    }
    setObservations(prev => prev.map(obs => (obs.id === id ? { ...obs, [field]: value } : obs)));
  };

  const handleCometNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormError(null);
    if (fieldErrors['cometName']) {
      const newErrors = { ...fieldErrors };
      delete newErrors['cometName'];
      setFieldErrors(newErrors);
    }
    setCometName(event.target.value);
  };
  
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        setPreviewUrl(result);
        setImageBase64(result.split(',')[1]);
      };
      reader.readAsDataURL(file);
    } else {
      setPreviewUrl(null);
      setImageBase64(null);
    }
  };
  
  // --- ФУНКЦИЯ ВАЛИДАЦИИ И ОТПРАВКИ ---
  const handleCalculate = async () => {
    // Валидация
    if (observations.length < 5) {
      setFormError('Необходимо как минимум 5 строк наблюдений.');
      setFieldErrors({});
      return;
    }
    const newErrors: FieldErrors = {};
    let hasError = false;
    observations.forEach(obs => {
      if (!obs.time) { newErrors[`${obs.id}-time`] = 'Заполните'; hasError = true; }
      if (!obs.ra.trim()) { newErrors[`${obs.id}-ra`] = 'Заполните'; hasError = true; }
      else if (isNaN(parseFloat(obs.ra))) { newErrors[`${obs.id}-ra`] = 'Неверный формат'; hasError = true; }
      if (!obs.dec.trim()) { newErrors[`${obs.id}-dec`] = 'Заполните'; hasError = true; }
      else if (isNaN(parseFloat(obs.dec))) { newErrors[`${obs.id}-dec`] = 'Неверный формат'; hasError = true; }
    });
    if (!cometName.trim()) { newErrors['cometName'] = 'Это поле обязательно'; hasError = true; }
    setFieldErrors(newErrors);
    if (hasError) { setFormError(null); return; }
    
    // Подготовка и отправка
    setFormError(null);
    setFieldErrors({});
    setIsLoading(true);

    try {
      // Подготовка данных для бэкенда
      const backendObservations = observations.map(obs => ({
        observation_time: new Date(obs.time).toISOString(),
        ra: parseFloat(obs.ra),
        dec: parseFloat(obs.dec),
      }));

      // Отправка запроса
      const result = await calculateOrbit({
        observations: backendObservations,
        image_reference: imageBase64,
        comet_uuid: cometName.trim(),
      });
      
      console.log('Расчет успешно запущен! ID задачи:', result.task_id);
      
      // Перенаправление на страницу результатов
      navigate(`/results/${result.task_id}`);

    } catch (error) {
      console.error('Ошибка при расчете:', error);
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
            accept="image/*"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          {previewUrl ? (
            <div className="image-preview-container">
              <img src={previewUrl} alt="Превью" className="image-preview" />
            </div>
          ) : (
            <div className="file-drop-zone" onClick={() => fileInputRef.current?.click()}>
              <span className="upload-icon">
                <svg width="61" height="60" viewBox="0 0 61 60" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path 
                    d="M30.4997 12.5V47.5M12.708 30H48.2913" 
                    stroke="#B3B3B3" 
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
              <span className="upload-text">Загрузите медиафайл</span>
            </div>
          )}
          <Input
            label="Название кометы"
            type="text"
            placeholder="Например, C/2023 A3"
            value={cometName}
            onChange={handleCometNameChange}
            className="comet-name-input"
            error={fieldErrors['cometName']}
          />
        </div>
      </div>
      
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