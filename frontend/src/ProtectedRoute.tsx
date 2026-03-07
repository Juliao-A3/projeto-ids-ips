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

  console.log("=== ProtectedRoute ===");
  console.log("token:", token);
  console.log("user:", user);
  console.log("allowedRoles:", allowedRoles);
  console.log("user.role:", user?.role);
  console.log("includes:", allowedRoles?.includes(user?.role ?? ""));

  if (!token) return <Navigate to="/login" replace />;
  if (!user) return null;

  if (allowedRoles && !allowedRoles.includes(user.role.toLowerCase())) {
    console.log("BLOQUEADO — role não permitido");
    return <Navigate to="/" replace />;
  }

  return children;
}