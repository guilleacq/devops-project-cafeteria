import { Navigate, Route, Routes } from "react-router-dom";

import AppShell from "./components/AppShell.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import BoardPage from "./pages/cafeteria/BoardPage.jsx";
import SalesPage from "./pages/cafeteria/SalesPage.jsx";
import SettingsPage from "./pages/cafeteria/SettingsPage.jsx";
import TodayPage from "./pages/cafeteria/TodayPage.jsx";
import MyOrdersPage from "./pages/student/MyOrdersPage.jsx";
import OrderPage from "./pages/student/OrderPage.jsx";
import { useSession } from "./session.jsx";

const STUDENT_TABS = [
  { to: "/pedir", label: "Pedir" },
  { to: "/mis-pedidos", label: "Mis pedidos" },
];

const CAFETERIA_TABS = [
  { to: "/cafeteria", label: "Próximo recreo", end: true },
  { to: "/cafeteria/hoy", label: "Pedidos de hoy" },
  { to: "/cafeteria/ventas", label: "Ventas" },
  { to: "/cafeteria/ajustes", label: "Ajustes" },
];

export default function App() {
  const { user, isLoading } = useSession();

  if (isLoading) return null;

  if (!user) {
    return (
      <Routes>
        <Route path="*" element={<LoginPage />} />
      </Routes>
    );
  }

  if (user.role === "cafeteria") {
    return (
      <Routes>
        <Route element={<AppShell tabs={CAFETERIA_TABS} wide />}>
          <Route path="/cafeteria" element={<BoardPage />} />
          <Route path="/cafeteria/hoy" element={<TodayPage />} />
          <Route path="/cafeteria/ventas" element={<SalesPage />} />
          <Route path="/cafeteria/ajustes" element={<SettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/cafeteria" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route element={<AppShell tabs={STUDENT_TABS} />}>
        <Route path="/pedir" element={<OrderPage />} />
        <Route path="/mis-pedidos" element={<MyOrdersPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/pedir" replace />} />
    </Routes>
  );
}
