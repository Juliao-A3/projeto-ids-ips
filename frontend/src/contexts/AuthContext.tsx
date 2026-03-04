import { createContext, useContext, useState, type ReactNode, useEffect } from "react";

type User = {
  name: string;
  role: string;
  initials: string;
} | null;

type AuthContextType = {
  user: User;
  setUser: (user: User) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User>(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const name = localStorage.getItem("user_name");
    const role = localStorage.getItem("user_role");

    if (token && name && role) {
      const initials = name
        .trim()
        .split(/\s+/)
        .filter((word: string) => word.length > 0)
        .map((word: string) => word[0])
        .join("")
        .toUpperCase()
        .slice(0, 2) || "U";

      setUser({
        name,
        role,
        initials
      });
    }
  }, []);

  const logout = () => {
    // Remove os tokens
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_name");
    localStorage.removeItem("user_role");

    // Limpa o estado do contexto
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);