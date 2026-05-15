import React, { useState } from 'react';
import { Table, Button, Space, Tag, Typography, Modal, Form, Input, Select, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';

const { Title } = Typography;
const { Option } = Select;

export default function AccountManagementPage() {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();

  // MOCK DATA: In the future, we will fetch this from Python!
  const [users, setUsers] = useState([
    { key: '1', name: 'Nguyễn Văn A', email: 'admin@mainplaza.com', role: 'admin', status: 'Hoạt động' },
    { key: '2', name: 'Ban Quản Lý', email: 'board@mainplaza.com', role: 'management', status: 'Hoạt động' },
    { key: '3', name: 'Trần Thị B', email: 'staff@mainplaza.com', role: 'staff', status: 'Hoạt động' },
    { key: '4', name: 'Starbucks', email: 'tenant@mainplaza.com', role: 'tenant', status: 'Tạm khóa' },
  ]);

  // COLOR CODING ROLES
  const roleColors = {
    admin: 'red',
    management: 'purple',
    staff: 'blue',
    tenant: 'green'
  };

  const roleLabels = {
    admin: 'Quản trị viên',
    management: 'Ban Quản Lý',
    staff: 'Nhân viên',
    tenant: 'Khách thuê'
  };

  const columns = [
    { title: 'Tên người dùng', dataIndex: 'name', key: 'name' },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { 
      title: 'Vai trò', 
      dataIndex: 'role', 
      key: 'role',
      render: (role) => <Tag color={roleColors[role]}>{roleLabels[role]}</Tag>
    },
    { 
      title: 'Trạng thái', 
      dataIndex: 'status', 
      key: 'status',
      render: (status) => <Tag color={status === 'Hoạt động' ? 'success' : 'error'}>{status}</Tag>
    },
    {
      title: 'Thao tác',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button type="text" icon={<EditOutlined />} style={{ color: '#1890ff' }} />
          <Button type="text" icon={<DeleteOutlined />} danger />
        </Space>
      ),
    },
  ];

  const handleAddUser = (values) => {
    // Add the new user to our local state table
    const newUser = {
      key: Date.now().toString(),
      name: values.name,
      email: values.email,
      role: values.role,
      status: 'Hoạt động'
    };
    setUsers([...users, newUser]);
    message.success('Đã thêm tài khoản mới!');
    setIsModalVisible(false);
    form.resetFields();
  };

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <Title level={3} style={{ margin: 0 }}>Quản lý Tài khoản</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalVisible(true)}>
          Thêm tài khoản
        </Button>
      </div>

      <Table 
        columns={columns} 
        dataSource={users} 
        style={{ backgroundColor: '#fff', borderRadius: '8px' }}
      />

      {/* ─── ADD USER MODAL ─── */}
      <Modal 
        title="Thêm tài khoản mới" 
        open={isModalVisible} 
        onCancel={() => {
          setIsModalVisible(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleAddUser} style={{ marginTop: '24px' }}>
          <Form.Item name="name" label="Tên người dùng" rules={[{ required: true, message: 'Vui lòng nhập tên!' }]}>
            <Input placeholder="Nhập họ và tên" />
          </Form.Item>
          
          <Form.Item name="email" label="Email đăng nhập" rules={[{ required: true, type: 'email', message: 'Vui lòng nhập email hợp lệ!' }]}>
            <Input placeholder="example@mainplaza.com" />
          </Form.Item>

          <Form.Item name="password" label="Mật khẩu khởi tạo" rules={[{ required: true, message: 'Vui lòng nhập mật khẩu!' }]}>
            <Input.Password placeholder="Nhập mật khẩu" />
          </Form.Item>

          <Form.Item name="role" label="Vai trò" rules={[{ required: true, message: 'Vui lòng chọn vai trò!' }]}>
            <Select placeholder="Chọn vai trò">
              <Option value="admin">Quản trị viên (Admin)</Option>
              <Option value="management">Ban Quản Lý (Board)</Option>
              <Option value="staff">Nhân viên (Staff)</Option>
              <Option value="tenant">Khách thuê (Tenant)</Option>
            </Select>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Button onClick={() => setIsModalVisible(false)} style={{ marginRight: '8px' }}>Hủy</Button>
            <Button type="primary" htmlType="submit">Tạo tài khoản</Button>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}