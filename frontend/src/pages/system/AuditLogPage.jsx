import React, { useState } from 'react';
import { Table, Typography, Tag, Space, DatePicker, Select, Input, Card } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

const { Title } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

export default function AuditLogPage() {
  // MOCK DATA: Simulating a backend database of system logs
  const [logs] = useState([
    { key: '1', time: '2023-10-25 09:15:22', user: 'Nguyễn Văn A (Admin)', action: 'Thêm tài khoản mới', module: 'System', status: 'Thành công', ip: '192.168.1.45' },
    { key: '2', time: '2023-10-25 08:30:00', user: 'Trần Thị B (Staff)', action: 'Cập nhật trạng thái hợp đồng', module: 'Contracts', status: 'Thành công', ip: '192.168.1.112' },
    { key: '3', time: '2023-10-24 16:45:10', user: 'Starbucks (Tenant)', action: 'Gửi yêu cầu bảo trì', module: 'Maintenance', status: 'Thành công', ip: '113.190.23.5' },
    { key: '4', time: '2023-10-24 14:20:05', user: 'Khách vô danh', action: 'Đăng nhập sai mật khẩu', module: 'Auth', status: 'Thất bại', ip: '45.22.19.102' },
    { key: '5', time: '2023-10-24 10:05:00', user: 'Ban Quản Lý', action: 'Duyệt yêu cầu thuê thêm', module: 'Approvals', status: 'Thành công', ip: '192.168.1.10' },
  ]);

  const moduleColors = {
    System: 'magenta',
    Contracts: 'blue',
    Maintenance: 'orange',
    Auth: 'red',
    Approvals: 'purple'
  };

  const columns = [
    { title: 'Thời gian', dataIndex: 'time', key: 'time', width: 180 },
    { title: 'Người dùng', dataIndex: 'user', key: 'user' },
    { title: 'Hành động', dataIndex: 'action', key: 'action' },
    { 
      title: 'Phân hệ', 
      dataIndex: 'module', 
      key: 'module',
      render: (mod) => <Tag color={moduleColors[mod]}>{mod}</Tag>
    },
    { title: 'IP Address', dataIndex: 'ip', key: 'ip' },
    { 
      title: 'Trạng thái', 
      dataIndex: 'status', 
      key: 'status',
      render: (status) => <Tag color={status === 'Thành công' ? 'success' : 'error'}>{status}</Tag>
    },
  ];

  return (
    <>
      <Title level={3} style={{ marginBottom: '24px' }}>Nhật ký thao tác (Audit Log)</Title>

      {/* ─── FILTER BAR ─── */}
      <Card bodyStyle={{ padding: '16px' }} style={{ marginBottom: '24px', borderRadius: '8px' }}>
        <Space wrap size="middle">
          <Input 
            placeholder="Tìm kiếm người dùng/hành động..." 
            prefix={<SearchOutlined />} 
            style={{ width: 300 }} 
          />
          <RangePicker style={{ width: 280 }} />
          <Select placeholder="Chọn phân hệ" style={{ width: 150 }} allowClear>
            <Option value="System">System</Option>
            <Option value="Auth">Auth</Option>
            <Option value="Contracts">Contracts</Option>
            <Option value="Finance">Finance</Option>
            <Option value="Maintenance">Maintenance</Option>
          </Select>
          <Select placeholder="Trạng thái" style={{ width: 120 }} allowClear>
            <Option value="success">Thành công</Option>
            <Option value="fail">Thất bại</Option>
          </Select>
        </Space>
      </Card>

      {/* ─── LOG TABLE ─── */}
      <Table 
        columns={columns} 
        dataSource={logs} 
        style={{ backgroundColor: '#fff', borderRadius: '8px' }}
        pagination={{ pageSize: 10 }}
        scroll={{ x: 1000 }}
      />
    </>
  );
}