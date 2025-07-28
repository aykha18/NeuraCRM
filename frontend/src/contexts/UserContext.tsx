import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  avatar_url?: string;
}

interface UserContextType {
  user: User | null;
  loading: boolean;
  setUser: (user: User | null) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching user data
    // In a real app, this would be an API call
    const fetchUser = async () => {
      try {
        // For now, use a mock user
        const mockUser: User = {
          id: 1,
          name: "Ayaan Khan",
          email: "ayaan.khan@neuracrm.com",
          role: "admin"
        };
        setUser(mockUser);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  return (
    <UserContext.Provider value={{ user, loading, setUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
} 