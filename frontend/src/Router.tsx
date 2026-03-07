import { Routes, Route } from "react-router-dom";
import ProtectedRoute  from "./ProtectedRoute";
import { PublicRoute } from "./PublicRoute";
import { ConfigLayout } from "./layouts/ConfigLayout";
import { DefaultLayout } from "./layouts/DefaultLayout";
import { AIModelSettings } from "./pages/AIModelSettings";
import { Dashboard } from "./pages/Dashboard";
import Login from "./pages/Login";
import { NetworkSettings } from "./pages/NetworkSettings";
import { NotificationsSettings } from "./pages/NotificationsSettings";
import { ReportsSettings } from "./pages/ReportsSettings";
import Setup from "./pages/Setup";
import { UserPage } from "./pages/UserPage";

export function Router() {
  return (
    <Routes>

      {/* ROTAS PÚBLICAS (login, setup) */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/setup"
        element={
          <PublicRoute>
            <Setup />
          </PublicRoute>
        }
      />

      {/* ROTAS PROTEGIDAS */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DefaultLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
      </Route>

      <Route
        path="/settings"
        element={
          <ProtectedRoute allowedRoles={["admin", "analista", "operador"]}>
            {/* operador removido daqui — só acede ao dashboard */}
            <ConfigLayout />
          </ProtectedRoute>
        }
      >
        <Route path="user" element={<ProtectedRoute allowedRoles={["admin"]}><UserPage /></ProtectedRoute>} />
        <Route path="ai-model" element={<ProtectedRoute allowedRoles={["admin", "analista"]}><AIModelSettings /></ProtectedRoute>} />
        <Route path="network" element={<ProtectedRoute allowedRoles={["admin", "analista"]}><NetworkSettings /></ProtectedRoute>} />
        <Route path="notifications" element={<ProtectedRoute allowedRoles={["admin"]}><NotificationsSettings /></ProtectedRoute>} />
        <Route path="relatorio" element={<ProtectedRoute allowedRoles={["admin", "analista", "operador"]}><ReportsSettings /></ProtectedRoute>} />
      </Route>

    </Routes>
  );
}