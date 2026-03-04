import type { JSX } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";

type Props = {
  children: JSX.Element;
  allowedRoles?: string[];
};

export default function ProtectedRoute({ children, allowedRoles }: Props) {
  const token = localStorage.getItem("access_token");
  const { user } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        <h2>Acesso Denegado</h2>
        <p>Você não tem permissão para acessar esta página.</p>
        <a href="/">Voltar ao Dashboard</a>
      </div>
    );
  }

  return children;
}