import React from 'react';

import Header from '../../widgets/Header/ui/Header';
import HeroSection from '../../widgets/HeroSection/ui/HeroSection';
import FactsCarousel from '../../widgets/FactsCarousel/ui/FactsCarousel';
import Footer from '../../widgets/Footer/ui/Footer'; 

const HomePage: React.FC = () => {
  return (
    <>
      <Header />
      <main>
        <HeroSection />
        <FactsCarousel />
        {/* Будущий контент страницы будет здесь */}
      </main>
      <Footer /> 
    </>
  );
};

export default HomePage;