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

const DynamicSpheres: React.FC = () => {
  return (
    <Canvas camera={{ position: [0, 0, 5] }}>
      <ambientLight intensity={0.5} />
      
      <DottedSphere 
        size={3}
        rotationSpeed={0.5} 
        position={[-4, 0, 0]}
        animationOffset={0}
      />
      
      <DottedSphere 
        size={1.5} 
        rotationSpeed={-0.8}
        position={[-1.5, 0, 1]}
        animationOffset={1.5} 
      />
      
      <DottedSphere 
        size={1.5} 
        rotationSpeed={0.3}
        position={[4.5, -2.5, 1]}
        animationOffset={3} 
      />
    </Canvas>
  );
};

export default DynamicSpheres;