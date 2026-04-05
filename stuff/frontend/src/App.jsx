import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";

import DashboardPage from "./pages/DashboardPage";
import HomePage from "./pages/HomePage";
import ItemDetailPage from "./pages/ItemDetailPage";
import LocationDetailPage from "./pages/LocationDetailPage";
import { clearToken, isAuthenticated } from "./auth";

function ProtectedRoute({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/" replace />;
  }
  return children;
}

function AppShell({ children }) {
  const navigate = useNavigate();

  function handleLogout() {
    clearToken();
    navigate("/");
  }

  return (
    <div className="shell">
      <header className="app-header">
        <Link to="/app" className="brand">
          Stuff Atlas
        </Link>
        <button type="button" className="btn ghost" onClick={handleLogout}>
          Logout
        </button>
      </header>
      <main className="app-main">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <AppShell>
              <DashboardPage />
            </AppShell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/locations/:locationId"
        element={
          <ProtectedRoute>
            <AppShell>
              <LocationDetailPage />
            </AppShell>
          </ProtectedRoute>
        }
      />
      <Route
        path="/items/:itemId"
        element={
          <ProtectedRoute>
            <AppShell>
              <ItemDetailPage />
            </AppShell>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
