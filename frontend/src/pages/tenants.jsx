import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layout, Menu, Card, Table, Typography, Row, Col,
  Input, InputNumber, Avatar, Badge, Button, Tag, Modal, Form, Select,
  message, Space, Popconfirm
} from 'antd';
import {
  DashboardOutlined, ShopOutlined, FileTextOutlined,
  ToolOutlined, DollarOutlined, LogoutOutlined,
  QuestionCircleOutlined, BellOutlined, SettingOutlined,
  SearchOutlined, ArrowUpOutlined, PlusOutlined, EditOutlined, DeleteOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;
const { Option } = Select;

export default function TenantsPage() {
  const navigate = useNavigate();
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingTenant, setEditingTenant] = useState(null);
  const [form] = Form.useForm();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  // Fetch tenants from API
  const fetchTenants = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/tenants');
      setTenants(response.data.items || []);
    } catch (error) {
      message.error('Không thể tải danh sách mặt bằng');
      console.error(error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchTenants();
  }, []);

  // Handle create/edit tenant
  const handleSubmit = async (values) => {
    try {
      if (editingTenant) {
        await axios.put(`http://localhost:8000/tenants/${editingTenant.id}`, values);
        message.success('Cập nhật mặt bằng thành công');
      } else {
        await axios.post('http://localhost:8000/tenants', values);
        message.success('Thêm mặt bằng thành công');
      }
      setIsModalVisible(false);
      form.resetFields();
      setEditingTenant(null);
      fetchTenants();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  // Handle delete tenant
  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/tenants/${id}`);
      message.success('Xóa mặt bằng thành công');
      fetchTenants();
    } catch (error) {
      message.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  // Open modal for create
  const showCreateModal = () => {
    setEditingTenant(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  // Open modal for edit
  const showEditModal = (tenant) => {
    setEditingTenant(tenant);
    form.setFieldsValue({
      ...tenant,
      floor: tenant.floor,
      area: tenant.area,
    });
    setIsModalVisible(true);
  };

  // Sidebar Menu Configuration
  const menuItems = [
    { key: '1', icon: <DashboardOutlined />, label: 'Dashboard', onClick: () => navigate('/') },
    { key: '2', icon: <ShopOutlined />, label: 'Tenants' },
    { key: '3', icon: <FileTextOutlined />, label: 'Leases' },
    { key: '4', icon: <ToolOutlined />, label: 'Maintenance' },
    { key: '5', icon: <DollarOutlined />, label: 'Financials' },
  ];

  const bottomMenuItems = [
    { key: 'help', icon: <QuestionCircleOutlined />, label: 'Help Center' },
    { key: 'logout', icon: <LogoutOutlined />, label: 'Logout', onClick: handleLogout },
  ];

  // Table columns
  const columns = [
    {
      title: 'Mã mặt bằng',
      dataIndex: 'code',
      key: 'code',
      sorter: (a, b) => a.code.localeCompare(b.code),
    },
    {
      title: 'Vị trí',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: 'Tầng',
      dataIndex: 'floor',
      key: 'floor',
      sorter: (a, b) => a.floor - b.floor,
    },
    {
      title: 'Diện tích (m²)',
      dataIndex: 'area',
      key: 'area',
      sorter: (a, b) => a.area - b.area,
    },
    {
      title: 'Loại mặt bằng',
      dataIndex: 'tenant_type',
      key: 'tenant_type',
      filters: [
        { text: 'Cửa hàng', value: 'Cửa hàng' },
        { text: 'Văn phòng', value: 'Văn phòng' },
        { text: 'Nhà hàng', value: 'Nhà hàng' },
        { text: 'Khác', value: 'Khác' },
      ],
      onFilter: (value, record) => record.tenant_type === value,
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const color = status === 'Còn trống' ? 'green' :
                     status === 'Đang thuê' ? 'red' :
                     status === 'Đang bảo trì' ? 'orange' : 'default';
        return <Tag color={color}>{status}</Tag>;
      },
      filters: [
        { text: 'Còn trống', value: 'Còn trống' },
        { text: 'Đang thuê', value: 'Đang thuê' },
        { text: 'Đang bảo trì', value: 'Đang bảo trì' },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: 'Thao tác',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => showEditModal(record)}
          >
            Sửa
          </Button>
          <Popconfirm
            title="Bạn có chắc muốn xóa mặt bằng này?"
            onConfirm={() => handleDelete(record.id)}
            okText="Xóa"
            cancelText="Hủy"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              disabled={record.status === 'Đang thuê'}
            >
              Xóa
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={250}
        theme="light"
        breakpoint="lg"
        collapsedWidth="0"
        onBreakpoint={(broken) => setIsMobile(broken)}
        style={{
          borderRight: '1px solid #f0f0f0',
          position: isMobile ? 'absolute' : 'relative',
          height: '100vh',
          zIndex: 999,
          background: '#fff'
        }}
      >
        <div style={{ padding: '24px 20px', borderBottom: '1px solid #f0f0f0' }}>
          <Title level={4} style={{ margin: 0, color: '#1890ff' }}>MallAdmin Pro</Title>
          <Text type="secondary" style={{ fontSize: '12px' }}>Management Suite</Text>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100% - 76px)' }}>
          <Menu
            theme="light"
            mode="inline"
            selectedKeys={['2']}
            items={menuItems}
            style={{ borderRight: 0, flex: 1, padding: '16px 0' }}
          />
          <div style={{ borderTop: '1px solid #f0f0f0' }}>
            <Menu
              theme="light"
              mode="inline"
              selectable={false}
              items={bottomMenuItems}
              style={{ borderRight: 0, padding: '16px 0' }}
            />
          </div>
        </div>
      </Sider>

      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ margin: 0 }}>Quản lý mặt bằng</Title>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Badge count={0}>
              <BellOutlined style={{ fontSize: '18px' }} />
            </Badge>
            <Avatar style={{ backgroundColor: '#1890ff' }}>A</Avatar>
          </div>
        </Header>

        <Content style={{ margin: '24px 16px 0' }}>
          <div style={{ padding: 24, background: '#fff', minHeight: 360 }}>
            <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
              <Col>
                <Title level={4}>Danh sách mặt bằng</Title>
              </Col>
              <Col>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={showCreateModal}
                >
                  Thêm mặt bằng
                </Button>
              </Col>
            </Row>

            <Table
              columns={columns}
              dataSource={tenants}
              loading={loading}
              rowKey="id"
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `${range[0]}-${range[1]} của ${total} mặt bằng`,
              }}
            />
          </div>
        </Content>
      </Layout>

      {/* Modal for Create/Edit */}
      <Modal
        title={editingTenant ? "Sửa mặt bằng" : "Thêm mặt bằng"}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          form.resetFields();
          setEditingTenant(null);
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="code"
            label="Mã mặt bằng"
            rules={[{ required: true, message: 'Vui lòng nhập mã mặt bằng' }]}
          >
            <Input placeholder="Ví dụ: MB001" />
          </Form.Item>

          <Form.Item
            name="location"
            label="Vị trí"
            rules={[{ required: true, message: 'Vui lòng nhập vị trí' }]}
          >
            <Input placeholder="Ví dụ: Tầng 1, Khu A" />
          </Form.Item>

          <Form.Item
            name="floor"
            label="Tầng"
            rules={[{ required: true, message: 'Vui lòng nhập tầng' }]}
          >
              <InputNumber style={{ width: '100%' }} min={0} placeholder="Ví dụ: 1" />
            </Form.Item>

            <Form.Item
              name="area"
              label="Diện tích (m²)"
              rules={[
                { required: true, message: 'Vui lòng nhập diện tích' },
                { type: 'number', min: 0.01, message: 'Diện tích phải lớn hơn 0' }
              ]}
            >
              <InputNumber style={{ width: '100%' }} min={0.01} step={0.01} placeholder="Ví dụ: 50.5" />
            </Form.Item>

            <Form.Item
              name="tenant_type"
              label="Loại mặt bằng"
              rules={[{ required: true, message: 'Vui lòng chọn loại mặt bằng' }]}
            >
              <Select placeholder="Chọn loại mặt bằng">
                <Option value="Cửa hàng">Cửa hàng</Option>
                <Option value="Văn phòng">Văn phòng</Option>
                <Option value="Nhà hàng">Nhà hàng</Option>
                <Option value="Khác">Khác</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="status"
              label="Trạng thái"
              rules={[{ required: true, message: 'Vui lòng chọn trạng thái' }]}
            >
            <Select placeholder="Chọn trạng thái">
              <Option value="Còn trống">Còn trống</Option>
              <Option value="Đang thuê">Đang thuê</Option>
              <Option value="Đang bảo trì">Đang bảo trì</Option>
            </Select>
          </Form.Item>

          <Form.Item style={{ textAlign: 'right', marginBottom: 0 }}>
            <Space>
              <Button onClick={() => {
                setIsModalVisible(false);
                form.resetFields();
                setEditingTenant(null);
              }}>
                Hủy
              </Button>
              <Button type="primary" htmlType="submit">
                {editingTenant ? 'Cập nhật' : 'Thêm'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
}