import React from 'react';
import HeroSection from '../../widgets/HeroSection/ui/HeroSection';
import FactsCarousel from '../../widgets/FactsCarousel/ui/FactsCarousel';

const HomePage: React.FC = () => {
  return (
    <> 
      <HeroSection />
      <FactsCarousel />
    </>
  );
};

export default HomePage;