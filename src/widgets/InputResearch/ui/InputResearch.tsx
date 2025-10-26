import { useNavigate } from 'react-router-dom';
import React, { useState, useRef, useEffect } from 'react';
import './InputResearch.css';
import { Button } from '../../../shared/ui/Button';

interface Observation {
  id: number;       // Уникальный идентификатор для ключей в React и для удаления
  time: string;     // Время наблюдения
  ra: string;       // Right Ascension (Прямое восхождение)
  dec: string;      // Declination (Склонение)
}

const generateInitialRows = (): Observation[] => {
  return Array.from({ length: 5 }, (_, i) => ({
    id: Date.now() + i, 
    time: '',
    ra: '',
    dec: '',
  }));
};

export const InputResearch: React.FC = () => {
  const navigate = useNavigate();
  const [observations, setObservations] = useState<Observation[]>(generateInitialRows());
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null); 
  useEffect(() => {
    return () => {
      previews.forEach(previewUrl => URL.revokeObjectURL(previewUrl));
    };
  }, [previews]);
  const handleAddRow = () => {
    const newRow: Observation = { id: Date.now(), time: '', ra: '', dec: '' };
    setObservations(prev => [...prev, newRow]);
  };

  const handleDeleteRow = (id: number) => {
    if (observations.length > 1) { 
      setObservations(prev => prev.filter(obs => obs.id !== id));
    }
  };

  const handleInputChange = (id: number, field: keyof Omit<Observation, 'id'>, value: string) => {
    setObservations(prev =>
      prev.map(obs => (obs.id === id ? { ...obs, [field]: value } : obs))
    );
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const newFiles = Array.from(event.target.files);
      const newPreviews = newFiles.map(file => URL.createObjectURL(file));
      
      setFiles(prev => [...prev, ...newFiles]);
      setPreviews(prev => [...prev, ...newPreviews]);
    }
  };
  
  const handleCalculate = () => {
    console.log("Введенные наблюдения:", observations);
    console.log("Загруженные файлы:", files);
    navigate('/results'); // ПЕРЕХОД НА СТРАНИЦУ РЕЗУЛЬТАТОВ
  };
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
            {observations.map((obs, index) => (
              <div key={obs.id} className="observation-row">
                <span className="row-number">{index + 1}</span>
                <input
                  type="text"
                  placeholder="..."
                  value={obs.time}
                  onChange={(e) => handleInputChange(obs.id, 'time', e.target.value)}
                  className="obs-input"
                />
                <input
                  type="text"
                  placeholder="..."
                  value={obs.ra}
                  onChange={(e) => handleInputChange(obs.id, 'ra', e.target.value)}
                  className="obs-input"
                />
                <input
                  type="text"
                  placeholder="..."
                  value={obs.dec}
                  onChange={(e) => handleInputChange(obs.id, 'dec', e.target.value)}
                  className="obs-input"
                />
                <button onClick={() => handleDeleteRow(obs.id)} className="delete-row-button">-</button>
              </div>
            ))}
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
              <span className="upload-icon">📷</span>
              <span className="upload-text">Загрузите медиафайлы</span>
              <span className="upload-hint">или перетащите их сюда</span>
            </div>
          )}
        </div>
      </div>

      <Button size="lg" className="calculate-button" onClick={handleCalculate}>
        Рассчитать координаты
      </Button>
    </div>
  );
};