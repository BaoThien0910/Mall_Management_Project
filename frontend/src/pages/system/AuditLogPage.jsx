import React, { useState } from 'react';
import { Table, Typography, Tag, Space, DatePicker, Select, Input, Card } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

const { Title } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

const MODULE_LABELS = {
  system: 'Hệ thống',
  auth: 'Xác thực',
  contracts: 'Hợp đồng',
  finance: 'Tài chính',
  maintenance: 'Bảo trì',
  approvals: 'Phê duyệt',
};

const MODULE_COLORS = {
  system: 'magenta',
  auth: 'red',
  contracts: 'blue',
  finance: 'green',
  maintenance: 'orange',
  approvals: 'purple',
};

export default function AuditLogPage() {
  const [logs] = useState([
    {
      key: '1',
      time: '2023-10-25 09:15:22',
      user: 'Nguyễn Văn A (Quản trị)',
      action: 'Thêm tài khoản mới',
      module: 'system',
      status: 'Thành công',
      ip: '192.168.1.45',
    },
    {
      key: '2',
      time: '2023-10-25 08:30:00',
      user: 'Trần Thị B (Nhân viên)',
      action: 'Cập nhật trạng thái hợp đồng',
      module: 'contracts',
      status: 'Thành công',
      ip: '192.168.1.112',
    },
    {
      key: '3',
      time: '2023-10-24 16:45:10',
      user: 'Starbucks (Khách thuê)',
      action: 'Gửi yêu cầu bảo trì',
      module: 'maintenance',
      status: 'Thành công',
      ip: '113.190.23.5',
    },
    {
      key: '4',
      time: '2023-10-24 14:20:05',
      user: 'Khách vô danh',
      action: 'Đăng nhập sai mật khẩu',
      module: 'auth',
      status: 'Thất bại',
      ip: '45.22.19.102',
    },
    {
      key: '5',
      time: '2023-10-24 10:05:00',
      user: 'Ban Quản Lý',
      action: 'Duyệt yêu cầu thuê thêm',
      module: 'approvals',
      status: 'Thành công',
      ip: '192.168.1.10',
    },
  ]);

  const columns = [
    { title: 'Thời gian', dataIndex: 'time', key: 'time', width: 180 },
    { title: 'Người dùng', dataIndex: 'user', key: 'user' },
    { title: 'Hành động', dataIndex: 'action', key: 'action' },
    {
      title: 'Phân hệ',
      dataIndex: 'module',
      key: 'module',
      render: (mod) => (
        <Tag color={MODULE_COLORS[mod]}>{MODULE_LABELS[mod] || mod}</Tag>
      ),
    },
    { title: 'Địa chỉ IP', dataIndex: 'ip', key: 'ip' },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'Thành công' ? 'success' : 'error'}>{status}</Tag>
      ),
    },
  ];

  return (
    <>
      <Title level={3} style={{ marginBottom: '24px' }}>
        Nhật ký thao tác
      </Title>

      <Card styles={{ body: { padding: '16px' } }} style={{ marginBottom: '24px', borderRadius: '8px' }}>
        <Space wrap size="middle">
          <Input
            placeholder="Tìm kiếm người dùng/hành động..."
            prefix={<SearchOutlined />}
            style={{ width: 300 }}
          />
          <RangePicker style={{ width: 280 }} placeholder={['Từ ngày', 'Đến ngày']} />
          <Select placeholder="Chọn phân hệ" style={{ width: 160 }} allowClear>
            {Object.entries(MODULE_LABELS).map(([value, label]) => (
              <Option key={value} value={value}>
                {label}
              </Option>
            ))}
          </Select>
          <Select placeholder="Trạng thái" style={{ width: 140 }} allowClear>
            <Option value="success">Thành công</Option>
            <Option value="fail">Thất bại</Option>
          </Select>
        </Space>
      </Card>

      <Table
        columns={columns}
        dataSource={logs}
        style={{ backgroundColor: '#fff', borderRadius: '8px' }}
        pagination={{ pageSize: 10, showTotal: (t) => `Tổng ${t} bản ghi` }}
        scroll={{ x: 1000 }}
      />
    </>
  );
}
