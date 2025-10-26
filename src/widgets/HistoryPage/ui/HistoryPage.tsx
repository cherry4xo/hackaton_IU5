import React from 'react';
// Импортируем стили специально для этого компонента
import styles from './HistoryPage.module.css';

// Данные для рендеринга. В реальном приложении они будут приходить из state или API.
const timelineData = [
    {
        date: '20.09.2001',
        items: [
            { id: 1, title: 'Комета Озон VS ВБ', time: '12:48:34' },
        ],
    },
    {
        date: '19.02.2001',
        items: [
            { id: 2, title: 'Комета 563HU72J', time: '13:28:35' },
            { id: 3, title: 'Комета 567CFR45', time: '13:17:25' },
        ],
    },
];

// Компонент страницы "Мои наблюдения"
const HistoryPage: React.FC = () => {
    return (
        // Главный контейнер для центрирования контента на странице
        <div className={styles.container}>
            <div className={styles.breadcrumbs}>
                <span>История</span> &gt; <a href="#">Мои наблюдения</a>
            </div>

            <div className={styles.timeline}>
                <button className={styles.dateRange}>
                    {/* Можно добавить иконку календаря в span */}
                    <span /> 
                    19.02.96 – 28.05.29 v
                </button>

                {/* Динамически рендерим группы наблюдений по датам */}
                {timelineData.map((group) => (
                    <div key={group.date} className={styles.timelineGroup}>
                        <div className={styles.timelineDate}>{group.date}</div>
                        
                        {/* Рендерим карточки внутри каждой группы */}
                        {group.items.map((item) => (
                            <div key={item.id} className={styles.timelineItem}>
                                <div className={styles.card}>
                                    <div className={styles.cardContent}>
                                        <h3>{item.title}</h3>
                                        <p>{item.time}</p>
                                    </div>
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