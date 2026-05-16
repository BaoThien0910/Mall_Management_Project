import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/auth/LoginPage';
import UnauthorizedPage from './pages/UnauthorizedPage';
import AccountManagementPage from './pages/system/AccountManagementPage';
import AuditLogPage from './pages/system/AuditLogPage';
import DebtListPage from './pages/finance/DebtListPage';
import DebtDetailPage from './pages/finance/DebtDetailPage';
import PaymentPage from './pages/finance/PaymentPage';
import PaymentResultPage from './pages/finance/PaymentResultPage';
import InvoiceHistoryPage from './pages/finance/InvoiceHistoryPage';
import FinancialImportPage from './pages/finance/FinancialImportPage';
import MaintenanceDashboard from './pages/maintenance/MaintenanceDashboard';
import MaintenanceDetailPage from './pages/maintenance/MaintenanceDetailPage';
import CreateMaintenanceRequest from './pages/maintenance/CreateMaintenanceRequest';
import MaintenanceScheduleCalendar from './pages/maintenance/MaintenanceScheduleCalendar';
import ReportsDashboard from './pages/reports/ReportsDashboard';
import AnnouncementsPage from './pages/notifications/AnnouncementsPage';
import ComingSoonPage from './pages/placeholders/ComingSoonPage';
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
        <Route path="/login" element={<LoginPage />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="accounts" element={<AccountManagementPage />} />
            <Route path="logs" element={<AuditLogPage />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute allowedRoles={['tenant']} />}>
          <Route path="/tenant" element={<TenantLayout />}>
            <Route
              index
              element={<ComingSoonPage title="Trang chủ khách thuê" description="Tổng quan gian hàng và thông báo." />}
            />
            <Route
              path="contract"
              element={<ComingSoonPage title="Hợp đồng của tôi" description="Xem và tải hợp đồng thuê mặt bằng." />}
            />
            <Route path="billing" element={<DebtListPage />} />
            <Route path="billing/invoices" element={<InvoiceHistoryPage />} />
            <Route path="billing/pay/result" element={<PaymentResultPage />} />
            <Route path="billing/pay/:id" element={<PaymentPage />} />
            <Route path="billing/:id" element={<DebtDetailPage />} />
            <Route path="maintenance" element={<MaintenanceDashboard />} />
            <Route path="maintenance/new" element={<CreateMaintenanceRequest />} />
            <Route path="maintenance/:id" element={<MaintenanceDetailPage />} />
            <Route path="maintenance/schedule/calendar" element={<MaintenanceScheduleCalendar />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute allowedRoles={['staff']} />}>
          <Route path="/staff" element={<StaffLayout />}>
            <Route
              index
              element={<ComingSoonPage title="Bàn làm việc nhân viên" description="Việc cần làm và thông báo nội bộ." />}
            />
            <Route
              path="premises"
              element={<ComingSoonPage title="Quản lý mặt bằng" description="Danh mục mặt bằng, trạng thái và chỉ số." />}
            />
            <Route
              path="contracts"
              element={<ComingSoonPage title="Quản lý hợp đồng" description="Số hóa hợp đồng, trạng thái và phụ lục." />}
            />
            <Route path="finance" element={<DebtListPage />} />
            <Route path="finance/import" element={<FinancialImportPage />} />
            <Route path="finance/invoices" element={<InvoiceHistoryPage />} />
            <Route path="finance/:id" element={<DebtDetailPage />} />
            <Route path="maintenance" element={<MaintenanceDashboard />} />
            <Route path="maintenance/new" element={<CreateMaintenanceRequest />} />
            <Route path="maintenance/:id" element={<MaintenanceDetailPage />} />
            <Route path="maintenance/schedule/calendar" element={<MaintenanceScheduleCalendar />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute allowedRoles={['management']} />}>
          <Route path="/management" element={<ManagementLayout />}>
            <Route
              index
              element={<ComingSoonPage title="Ban quản lý" description="Dashboard phê duyệt và ra quyết định." />}
            />
            <Route path="approvals" element={<ComingSoonPage title="Phê duyệt yêu cầu" description="Thuê thêm, sự cố và các quyết định." />} />
            <Route path="reports" element={<ReportsDashboard />} />
            <Route path="announcements" element={<AnnouncementsPage />} />
          </Route>
        </Route>

        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
