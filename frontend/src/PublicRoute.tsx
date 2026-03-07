import type { JSX } from "react";
import { Navigate } from "react-router-dom";

export function PublicRoute({ children }: { children: JSX.Element }) {
  const token = localStorage.getItem("access_token");

  // Se o usuário está logado, redireciona para dashboard
  if (token) {
    return <Navigate to="/" replace />;
  }

  return children;
}