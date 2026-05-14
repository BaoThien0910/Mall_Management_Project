import React from 'react';
import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';

export default function UnauthorizedPage() {
  const navigate = useNavigate();
  return (
    <Result
      status="403"
      title="403 - Không có quyền truy cập"
      subTitle="Xin lỗi, bạn không có quyền truy cập vào trang này."
      extra={<Button type="primary" onClick={() => navigate(-1)}>Quay lại</Button>}
    />
  );
}