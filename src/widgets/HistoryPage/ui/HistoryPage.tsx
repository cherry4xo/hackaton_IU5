import React, { useState, forwardRef } from 'react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

// --- ИЗМЕНЕНИЕ 1: Импортируем иконки ---
import { FiCalendar, FiChevronDown } from 'react-icons/fi';

import styles from './HistoryPage.module.css';
import './CustomCalendar.css'; 

const timelineData = [
    { date: '20.09.2001', items: [{ id: 1, title: 'Комета Озон VS ВБ', time: '12:48:34' }] },
    { date: '19.02.2001', items: [{ id: 2, title: 'Комета 563HU72J', time: '13:28:35' }, { id: 3, title: 'Комета 567CFR45', time: '13:17:25' }] },
];

// --- ИЗМЕНЕНИЕ 2: Обновляем внутреннюю структуру кнопки ---
const CustomDateInput = forwardRef<HTMLButtonElement, { value?: string; onClick?: () => void }>(
  ({ value, onClick }, ref) => (
    // Весь `onClick` вешается на саму кнопку, поэтому клик по любой её части (иконкам, тексту) будет работать
    <button className={styles.dateRange} onClick={onClick} ref={ref}>
      <FiCalendar size={18} />
      {/* Оборачиваем текст в span, чтобы управлять отступами */}
      <span className={styles.dateText}>{value}</span>
      <FiChevronDown size={20} />
    </button>
  )
);

export const HistoryPage: React.FC = () => {
  const [startDate, setStartDate] = useState<Date | null>(new Date("1996-02-19"));
  const [endDate, setEndDate] = useState<Date | null>(new Date("2029-05-28"));

  const handleDateChange = (dates: [Date | null, Date | null]) => {
    const [start, end] = dates;
    setStartDate(start);
    setEndDate(end);
  };

  return (
    <div className={styles.container}>
      <div className={styles.breadcrumbs}>
        <span>История</span> &gt; <a href="#">Мои наблюдения</a>
      </div>

      <div className={styles.timeline}>
        <DatePicker
          selected={startDate}
          onChange={handleDateChange}
          startDate={startDate}
          endDate={endDate}
          selectsRange
          dateFormat="dd.MM.yy"
          customInput={<CustomDateInput />}
          calendarClassName="custom-calendar"
        />

        {timelineData.map((group) => (
          <div key={group.date} className={styles.timelineGroup}>
            <div className={styles.timelineDate}>{group.date}</div>
            {group.items.map((item) => (
              <div key={item.id} className={styles.timelineItem}>
                <div className={styles.card}>
                  <div className={styles.cardContent}><h3>{item.title}</h3><p>{item.time}</p></div>
                  <a href="#" className={styles.cardAction}>Резы</a>
                </div>
              </div>
            ))}
          </div>
        ))}
        <div className={styles.endOfHistory}>Конец истории</div>
      </div>
    </div>
  );
};

export default HistoryPage;