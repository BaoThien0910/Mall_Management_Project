import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/auth/LoginPage';
import UnauthorizedPage from './pages/system/UnauthorizedPage';
import ProtectedRoute from './components/common/ProtectedRoute';

import AdminLayout from './layouts/AdminLayout';
import TenantLayout from './layouts/TenantLayout';
import StaffLayout from './layouts/StaffLayout';
import ManagementLayout from './layouts/ManagementLayout';
import DashboardPage from './pages/DashboardPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* PUBLIC ROUTES */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        {/* ─── PROTECTED ADMIN ROUTES ─── */}
        <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<DashboardPage />} />
          </Route>
        </Route>

        {/* ─── PROTECTED TENANT ROUTES ─── */}
        <Route element={<ProtectedRoute allowedRoles={['tenant']} />}>
          <Route path="/tenant" element={<TenantLayout />}>
            <Route index element={<h2>Tenant Dashboard</h2>} />
          </Route>
        </Route>

        {/* ─── PROTECTED STAFF ROUTES ─── */}
        <Route element={<ProtectedRoute allowedRoles={['staff']} />}>
          <Route path="/staff" element={<StaffLayout />}>
            <Route index element={<h2>Staff Dashboard</h2>} />
          </Route>
        </Route>

        {/* ─── PROTECTED MANAGEMENT ROUTES ─── */}
        <Route element={<ProtectedRoute allowedRoles={['management']} />}>
          <Route path="/management" element={<ManagementLayout />}>
            <Route index element={<h2>Management Dashboard</h2>} />
          </Route>
        </Route>

        {/* DEFAULT REDIRECT */}
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}