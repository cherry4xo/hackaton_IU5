import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame, RootState } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

interface DottedSphereProps {
  size: number;
  rotationSpeed: number;
  position: [number, number, number];
  animationOffset: number; 
}

const DottedSphere: React.FC<DottedSphereProps> = ({ size, rotationSpeed, position, animationOffset }) => {
  const pointsRef = useRef<THREE.Points | null>(null);

  const points = useMemo(() => {
    const geometry = new THREE.SphereGeometry(size, 48, 48);
    return geometry.attributes.position.array;
  }, [size]);

  useFrame((state: RootState) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += 0.001 * rotationSpeed;
      pointsRef.current.rotation.x += 0.0005 * rotationSpeed;
      const scale = 1 + Math.sin(state.clock.getElapsedTime() + animationOffset) * 0.02;
      pointsRef.current.scale.set(scale, scale, scale);
    }
  });

  return (
    <Points ref={pointsRef} position={position} positions={points as Float32Array} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#ffffff"
        size={0.02}
        sizeAttenuation={true}
        depthWrite={false}
      />
    </Points>
  );
};

// ... (импорты и компонент DottedSphere остаются без изменений) ...


const DynamicSpheres: React.FC = () => {
  return (
    // --- ИЗМЕНЕНИЕ 1: Настройка камеры для устранения искажений ---
    <Canvas camera={{ 
      position: [0, 0, 12], // Отодвигаем камеру дальше назад (было 5)
      fov: 30                  // Сужаем угол обзора, "приближая" сцену (было ~75 по умолчанию)
    }}>
      <ambientLight intensity={100.0} />
      
      {/* --- ИЗМЕНЕНИЕ 2: Новые позиции и размеры сфер --- */}
      
      {/* Сферы слева, смещенные еще дальше */}
      <DottedSphere 
        size={3.0} // Немного увеличил размер, т.к. камера дальше
        rotationSpeed={0.4} 
        position={[-7.5, 0, -2]} // Смещена сильно влево по оси X
        animationOffset={1}
      />
      
      <DottedSphere 
        size={2.2} // Немного увеличил
        rotationSpeed={-0.6}
        position={[-7, -1.5, 0]} // Также сильно слева
        animationOffset={1.5} 
      />
      
      {/* Сфера справа, смещенная еще дальше */}
      <DottedSphere 
        size={2.8} // Немного увеличил
        rotationSpeed={0.3}
        position={[8, 1.5, -1]} // Смещена сильно вправо по оси X
        animationOffset={3} 
      />
    </Canvas>
  );
};

export default DynamicSpheres;