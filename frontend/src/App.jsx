import { Spin } from "antd";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";

import AppShell from "./layouts/AppShell";
import { bootstrapAuth } from "./store/authSlice";
import { routePermissions, ROUTES } from "./constants/routes";

import LoginPage from "./pages/auth/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import AccountListPage from "./pages/system/AccountListPage";
import RbacPage from "./pages/system/RbacPage";
import AuditLogPage from "./pages/system/AuditLogPage";
import PremiseListPage from "./pages/premises/PremiseListPage";
import ContractListPage from "./pages/contracts/ContractListPage";
import MyContractsPage from "./pages/contracts/MyContractsPage";
import RentRequestPage from "./pages/contracts/RentRequestPage";
import DebtListPage from "./pages/finance/DebtListPage";
import MyDebtListPage from "./pages/finance/MyDebtListPage";
import PaymentPage from "./pages/finance/PaymentPage";
import FinancialImportPage from "./pages/finance/FinancialImportPage";
import FinancialReportPage from "./pages/reports/FinancialReportPage";
import IncidentListPage from "./pages/maintenance/IncidentListPage";
import MeterReadingPage from "./pages/maintenance/MeterReadingPage";
import ScheduleListPage from "./pages/maintenance/ScheduleListPage";
import MaintenanceReportPage from "./pages/reports/MaintenanceReportPage";
import NotificationListPage from "./pages/notifications/NotificationListPage";

function AuthBootstrap({ children }) {
  const dispatch = useDispatch();
  const { bootstrapped, loading } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(bootstrapAuth());
  }, [dispatch]);

  if (!bootstrapped && loading) {
    return (
      <div className="screen-loader">
        <Spin size="large" />
      </div>
    );
  }

  return children;
}

function getCurrentRole(user) {
  return (
    user?.ma_vai_tro ||
    user?.maVaiTro ||
    user?.mavaitro ||
    user?.role ||
    user?.vai_tro ||
    user?.tai_khoan?.ma_vai_tro ||
    user?.taiKhoan?.ma_vai_tro
  );
}

function ProtectedRoute({ allowedRoles }) {
  const { token, user, bootstrapped } = useSelector((state) => state.auth);
  const location = useLocation();

  if (!bootstrapped) {
    return (
      <div className="screen-loader">
        <Spin size="large" />
      </div>
    );
  }

  if (!token || !user) {
    return <Navigate to={ROUTES.LOGIN} replace state={{ from: location }} />;
  }

  const role = getCurrentRole(user);

  if (allowedRoles && allowedRoles.length > 0 && !allowedRoles.includes(role)) {
    return <Navigate to={ROUTES.DASHBOARD} replace />;
  }

  return <AppShell />;
}

function PublicLoginRoute() {
  const { token, user } = useSelector((state) => state.auth);

  if (token && user) return <Navigate to={ROUTES.DASHBOARD} replace />;

  return <LoginPage />;
}

function ProtectedPage({ route, element }) {
  return <Route path={route} element={<ProtectedRoute allowedRoles={routePermissions[route]} />}>{element}</Route>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path={ROUTES.LOGIN} element={<PublicLoginRoute />} />

      <Route element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.DASHBOARD]} />}>
        <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
        <Route path={ROUTES.ACCOUNTS} element={<AccountListPage />} />
        <Route path={ROUTES.RBAC} element={<RbacPage />} />
        <Route path={ROUTES.AUDIT} element={<AuditLogPage />} />
        <Route path={ROUTES.PREMISES} element={<PremiseListPage />} />
        <Route path={ROUTES.CONTRACTS} element={<ContractListPage />} />
        <Route path={ROUTES.MY_CONTRACTS} element={<MyContractsPage />} />
        <Route path={ROUTES.RENT_REQUESTS} element={<RentRequestPage />} />
        <Route path={ROUTES.DEBTS} element={<DebtListPage />} />
        <Route path={ROUTES.MY_DEBTS} element={<MyDebtListPage />} />
        <Route path={ROUTES.PAYMENT} element={<PaymentPage />} />
        <Route path={ROUTES.FINANCIAL_IMPORT} element={<FinancialImportPage />} />
        <Route path={ROUTES.FINANCIAL_REPORTS} element={<FinancialReportPage />} />
        <Route path={ROUTES.METER_READINGS} element={<MeterReadingPage />} />
        <Route path={ROUTES.INCIDENTS} element={<IncidentListPage />} />
        <Route path={ROUTES.MAINTENANCE_SCHEDULES} element={<ScheduleListPage />} />
        <Route path={ROUTES.MAINTENANCE_REPORTS} element={<MaintenanceReportPage />} />
        <Route path={ROUTES.NOTIFICATIONS} element={<NotificationListPage />} />
      </Route>

      <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthBootstrap>
        <AppRoutes />
      </AuthBootstrap>
    </BrowserRouter>
  );
}
