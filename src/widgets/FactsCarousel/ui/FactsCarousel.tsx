import React from 'react';
import Slider from 'react-slick';
import styles from './FactsCarousel.module.css';

import "slick-carousel/slick/slick.css"; 
import "slick-carousel/slick/slick-theme.css";

const facts = [
  {
    title: 'Тунгусский метеорит',
    description: 'В 1908 году взрыв над Сибирью, предположительно вызванный кометой или астероидом, повалил 80 миллионов деревьев на площади 2150 км².',
  },
  {
    title: 'Комета Галлея',
    description: 'Самая известная комета, возвращающаяся к Земле каждые 75–76 лет. В следующий раз ее можно будет наблюдать в 2061 году.',
  },
  {
    title: 'Состав комет',
    description: 'Кометы — это ледяные тела, состоящие из замороженных газов, камней и пыли. Их часто называют "грязными снежками".',
  },
  {
    title: 'Хвост кометы',
    description: 'У комет два хвоста: пылевой и ионный. Пылевой хвост изогнут и следует за орбитой, а ионный всегда направлен в сторону от Солнца.',
  },
  {
    title: 'Чиксулубский кратер',
    description: 'Считается, что 66 миллионов лет назад падение астероида или кометы создало этот кратер и вызвало массовое вымирание динозавров.',
  },
  {
    title: 'Скорость комет',
    description: 'Приближаясь к Солнцу, кометы могут развивать огромную скорость, достигающую сотен тысяч километров в час из-за гравитационного ускорения.',
  },
];

const FactsCarousel: React.FC = () => {
  const settings = {
    dots: true,
    infinite: true,
    speed: 1500, 
    slidesToShow: 3,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000, 
    cssEase: "linear",
    pauseOnHover: true,
    responsive: [ 
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 2,
        }
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 1,
        }
      }
    ]
  };

  return (
    <div className={styles.carouselContainer}>
      <h2 className={styles.carouselTitle}>Интересные факты</h2>
      <Slider {...settings}>
        {facts.map((fact, index) => (
          <div key={index} className={styles.cardContainer}>
            <div className={styles.card}>
              <h3 className={styles.cardTitle}>{fact.title}</h3>
              <p className={styles.cardDescription}>{fact.description}</p>
            </div>
          </div>
        ))}
      </Slider>
    </div>
  );
};

export default FactsCarousel;