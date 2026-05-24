import { Spin } from "antd";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
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
import ScheduleListPage from "./pages/maintenance/ScheduleListPage";
import MaintenanceReportPage from "./pages/reports/MaintenanceReportPage";
import NotificationListPage from "./pages/notifications/NotificationListPage";

function AuthBootstrap({ children }) {
  const dispatch = useDispatch();
  const { bootstrapped, loading } = useSelector((state) => state.auth);
  useEffect(() => { dispatch(bootstrapAuth()); }, [dispatch]);
  if (!bootstrapped && loading) return <div className="screen-loader"><Spin size="large" /></div>;
  return children;
}

function ProtectedRoute({ children, allowedRoles }) {
  const { token, user, bootstrapped } = useSelector((state) => state.auth);
  const location = useLocation();
  if (!bootstrapped) return <div className="screen-loader"><Spin /></div>;
  if (!token || !user) return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
  const role = user?.ma_vai_tro || user?.role;
  if (allowedRoles && !allowedRoles.includes(role)) return <Navigate to={ROUTES.DASHBOARD} replace />;
  return children;
}

function PublicLoginRoute() {
  const { token, user } = useSelector((state) => state.auth);
  if (token && user) return <Navigate to={ROUTES.DASHBOARD} replace />;
  return <LoginPage />;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthBootstrap>
        <Routes>
          <Route path={ROUTES.LOGIN} element={<PublicLoginRoute />} />
          <Route path="/" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.DASHBOARD]}><AppShell /></ProtectedRoute>}>
            <Route index element={<DashboardPage />} />
            <Route path="system/accounts" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.ACCOUNTS]}><AccountListPage /></ProtectedRoute>} />
            <Route path="system/rbac" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.RBAC]}><RbacPage /></ProtectedRoute>} />
            <Route path="system/audit" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.AUDIT]}><AuditLogPage /></ProtectedRoute>} />
            <Route path="premises" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.PREMISES]}><PremiseListPage /></ProtectedRoute>} />
            <Route path="contracts" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.CONTRACTS]}><ContractListPage /></ProtectedRoute>} />
            <Route path="contracts/cua-toi" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.MY_CONTRACTS]}><MyContractsPage /></ProtectedRoute>} />
            <Route path="yeu-cau-thue-them" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.RENT_REQUESTS]}><RentRequestPage /></ProtectedRoute>} />
            <Route path="finance/cong-no" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.DEBTS]}><DebtListPage /></ProtectedRoute>} />
            <Route path="finance/cong-no-cua-toi" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.MY_DEBTS]}><MyDebtListPage /></ProtectedRoute>} />
            <Route path="finance/thanh-toan" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.PAYMENT]}><PaymentPage /></ProtectedRoute>} />
            <Route path="finance/import" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.FINANCIAL_IMPORT]}><FinancialImportPage /></ProtectedRoute>} />
            <Route path="reports/financial" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.FINANCIAL_REPORTS]}><FinancialReportPage /></ProtectedRoute>} />
            <Route path="maintenance/su-co" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.INCIDENTS]}><IncidentListPage /></ProtectedRoute>} />
            <Route path="maintenance/lich-bao-tri" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.MAINTENANCE_SCHEDULES]}><ScheduleListPage /></ProtectedRoute>} />
            <Route path="reports/maintenance" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.MAINTENANCE_REPORTS]}><MaintenanceReportPage /></ProtectedRoute>} />
            <Route path="notifications" element={<ProtectedRoute allowedRoles={routePermissions[ROUTES.NOTIFICATIONS]}><NotificationListPage /></ProtectedRoute>} />
          </Route>
          <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
        </Routes>
      </AuthBootstrap>
    </BrowserRouter>
  );
}
