import { createContext, useContext, useState, type ReactNode } from "react";

type User = {
  name: string;
  role: string;
  initials: string;
};

type AuthContextType = {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: ReactNode }) {

  // lê do localStorage ao iniciar — resolve o problema do refresh
  const [user, setUser] = useState<User | null>(() => {
    const name = localStorage.getItem("user_name");
    const role = localStorage.getItem("user_role");
    const token = localStorage.getItem("access_token");

    if (!name || !role || !token) return null;

    const initials = name
      .trim()
      .split(/\s+/)
      .map(w => w[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);

    return { 
      name, 
      role: role.toLowerCase(), // normaliza aqui
      initials 
    };
  });

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_name");
    localStorage.removeItem("user_role");
    setUser(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);