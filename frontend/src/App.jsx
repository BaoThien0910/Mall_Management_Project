import { Spin, message } from "antd";
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
import { bootstrapAuth, logoutLocal } from "./store/authSlice";
import { routePermissions, ROUTES } from "./constants/routes";
import { parseJwt } from "./utils/storage";
import { registerLogoutCallback } from "./services/apiClient";

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
import MaintenanceReportPage from "./pages/reports/MaintenanceReportPage";
import NotificationListPage from "./pages/notifications/NotificationListPage";

function AuthBootstrap({ children }) {
  const dispatch = useDispatch();
  const { bootstrapped, loading, token } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(bootstrapAuth());
  }, [dispatch]);

  useEffect(() => {
    registerLogoutCallback(() => {
      dispatch(logoutLocal());
      message.warning("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
    });
  }, [dispatch]);

  useEffect(() => {
    if (!token) return undefined;

    const payload = parseJwt(token);
    if (!payload?.exp) return undefined;

    const delay = payload.exp * 1000 - Date.now();
    if (delay <= 0) {
      dispatch(logoutLocal());
      message.warning("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
      return undefined;
    }

    const timer = setTimeout(() => {
      dispatch(logoutLocal());
      message.warning("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.");
    }, delay);

    return () => clearTimeout(timer);
  }, [token, dispatch]);

  if (!bootstrapped && loading) {
    return <Spin fullscreen tip="Đang khởi tạo phiên đăng nhập..." />;
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
    return <Spin fullscreen tip="Đang kiểm tra phiên đăng nhập..." />;
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

function protectedRoute(route, element) {
  return (
    <Route element={<ProtectedRoute allowedRoles={routePermissions[route]} />}>
      <Route path={route} element={element} />
    </Route>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path={ROUTES.LOGIN} element={<PublicLoginRoute />} />

      {protectedRoute(ROUTES.DASHBOARD, <DashboardPage />)}
      {protectedRoute(ROUTES.ACCOUNTS, <AccountListPage />)}
      {protectedRoute(ROUTES.RBAC, <RbacPage />)}
      {protectedRoute(ROUTES.AUDIT, <AuditLogPage />)}
      {protectedRoute(ROUTES.PREMISES, <PremiseListPage />)}
      {protectedRoute(ROUTES.CONTRACTS, <ContractListPage />)}
      {protectedRoute(ROUTES.MY_CONTRACTS, <MyContractsPage />)}
      {protectedRoute(ROUTES.RENT_REQUESTS, <RentRequestPage />)}
      {protectedRoute(ROUTES.DEBTS, <DebtListPage />)}
      {protectedRoute(ROUTES.MY_DEBTS, <MyDebtListPage />)}
      {protectedRoute(ROUTES.PAYMENT, <PaymentPage />)}
      {protectedRoute(ROUTES.FINANCIAL_IMPORT, <FinancialImportPage />)}
      {protectedRoute(ROUTES.FINANCIAL_REPORTS, <FinancialReportPage />)}
      {protectedRoute(ROUTES.METER_READINGS, <MeterReadingPage />)}
      {protectedRoute(ROUTES.INCIDENTS, <IncidentListPage />)}
      {protectedRoute(ROUTES.MAINTENANCE_REPORTS, <MaintenanceReportPage />)}
      {protectedRoute(ROUTES.NOTIFICATIONS, <NotificationListPage />)}

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
