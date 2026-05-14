import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

export default function ProtectedRoute({ allowedRoles }) {
  // Đọc token và role từ "bộ nhớ phiên làm việc" (sessionStorage)
  const token = sessionStorage.getItem("token");
  const userRole = sessionStorage.getItem("role");

  // 1. Kiểm tra đăng nhập (Nếu không có token, đá về trang Login)
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // 2. Kiểm tra phân quyền (Nếu có token nhưng sai vai trò, đá về trang báo lỗi)
  if (allowedRoles && !allowedRoles.includes(userRole)) {
    return <Navigate to="/unauthorized" replace />;
  }

  // 3. Nếu hợp lệ, cho phép render Layout hoặc Page bên trong (Outlet)
  return <Outlet />;
}