import React, { createContext, useContext, useState, useEffect } from 'react';
import { getMe as apiGetMe } from '../../shared/api/auth';

// 1. Описываем, как выглядят данные пользователя
interface User {
  uuid: string;
  username: string;
  email: string;
  role: string;
}

// 2. Описываем, что будет храниться в нашем контексте
interface AuthContextType {
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
  isLoading: boolean;
  logout: () => void;
}

// 3. Создаем сам контекст
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 4. Создаем "Провайдер" - компонент-обертку
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true); // Загрузка при первом входе

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      apiGetMe(token)
        .then(userData => {
          setUser(userData);
        })
        .catch(() => {
          // Если токен невалидный, чистим хранилище
          localStorage.removeItem('accessToken');
          setUser(null);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false); // Если токена нет, просто заканчиваем загрузку
    }
  }, []);

  const logout = () => {
    localStorage.removeItem('accessToken');
    setUser(null);
  };

  const value = { user, setUser, isLoading, logout };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// 5. Создаем хук для удобного доступа к контексту
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};