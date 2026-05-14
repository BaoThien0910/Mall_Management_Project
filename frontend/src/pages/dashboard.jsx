import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Layout, Menu, Card, Table, Typography, Row, Col, 
  Input, Avatar, Badge, Button, Tag 
} from 'antd';
import { 
  DashboardOutlined, ShopOutlined, FileTextOutlined, 
  ToolOutlined, DollarOutlined, LogoutOutlined, 
  QuestionCircleOutlined, BellOutlined, SettingOutlined, 
  SearchOutlined, ArrowUpOutlined 
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

export default function Dashboard() {
  const navigate = useNavigate();
  const [isMobile, setIsMobile] = useState(false);
  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  // --- Sidebar Menu Configuration ---
  const menuItems = [
    { key: '1', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: '2', icon: <ShopOutlined />, label: 'Tenants' },
    { key: '3', icon: <FileTextOutlined />, label: 'Leases' },
    { key: '4', icon: <ToolOutlined />, label: 'Maintenance' },
    { key: '5', icon: <DollarOutlined />, label: 'Financials' },
  ];

  const bottomMenuItems = [
    { key: 'help', icon: <QuestionCircleOutlined />, label: 'Help Center' },
    { key: 'logout', icon: <LogoutOutlined />, label: 'Logout', onClick: handleLogout },
  ];

  // --- Table Data Configuration ---
  const tableColumns = [
    {
      title: 'Tenant',
      dataIndex: 'tenant',
      key: 'tenant',
      render: (text, record) => (
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <Text strong>{text}</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>{record.category}</Text>
        </div>
      )
    },
    { title: 'Unit', dataIndex: 'unit', key: 'unit' },
    { title: 'Expiry Date', dataIndex: 'date', key: 'date' },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        let color = status === 'URGENT' ? 'red' : 'volcano';
        return <Tag color={color}>{status}</Tag>;
      }
    },
    {
      title: 'Action',
      key: 'action',
      render: () => <Button size="small">Renew</Button>,
      align: 'right'
    },
  ];

  const tableData = [
    { key: '1', tenant: 'Starbucks', category: 'F&B', unit: 'GF-01', date: 'Oct 15, 2023', status: 'URGENT' },
    { key: '2', tenant: 'H&M', category: 'Fashion', unit: 'L1-12', date: 'Nov 02, 2023', status: 'WARNING' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      
      {/* ─── SIDEBAR ─── */}
      <Sider 
        width={250} 
        theme="light" 
        breakpoint="lg" 
        collapsedWidth="0"
        onBreakpoint={(broken) => setIsMobile(broken)} // Tracks if screen is mobile size
        style={{ 
            borderRight: '1px solid #f0f0f0',
            /* The Magic Fix: */
            position: isMobile ? 'absolute' : 'relative',
            height: '100vh',
            zIndex: 999, // Ensures it floats ON TOP of your charts
        }}
      >
        <div style={{ padding: '24px 20px', borderBottom: '1px solid #f0f0f0' }}>
          <Title level={4} style={{ margin: 0, color: '#1890ff' }}>MallAdmin Pro</Title>
          <Text type="secondary" style={{ fontSize: '12px' }}>Management Suite</Text>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100% - 76px)' }}>
          <Menu 
            mode="inline" 
            defaultSelectedKeys={['1']} 
            items={menuItems} 
            style={{ borderRight: 0, flex: 1, padding: '16px 0' }}
          />
          <Menu 
            mode="inline" 
            selectable={false} 
            items={bottomMenuItems} 
            style={{ borderRight: 0, borderTop: '1px solid #f0f0f0', padding: '16px 0' }}
          />
        </div>
      </Sider>

      {/* ─── MAIN LAYOUT ─── */}
      <Layout>
        
        {/* HEADER */}
        <Header style={{ background: '#fff', padding: '0 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #f0f0f0' }}>
          <Input 
            prefix={<SearchOutlined style={{ color: '#bfbfbf' }} />} 
            placeholder="Search tenants, leases, or tickets..." 
            style={{ width: 300, borderRadius: '20px' }} 
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <Badge dot><BellOutlined style={{ fontSize: '18px', cursor: 'pointer' }} /></Badge>
            <SettingOutlined style={{ fontSize: '18px', cursor: 'pointer' }} />
            <Avatar style={{ backgroundColor: '#1890ff' }}>A</Avatar>
          </div>
        </Header>

        {/* CONTENT */}
        <Content style={{ margin: '24px 32px', overflow: 'initial' }}>
          
          {/* Greeting */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
            <div>
              <Title level={2} style={{ margin: 0 }}>Chào buổi sáng, Admin</Title>
              <Text type="secondary">Here is what's happening at your property today.</Text>
            </div>
            <Button>📅 7 ngày qua</Button>
          </div>

          {/* KPI Cards */}
          {/* Replace your current KPI Row with this */}
          <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
        
        {/* Notice the responsive props: xs={24} (mobile), sm={12} (tablet), lg={6} (desktop) */}
            <Col xs={24} sm={12} lg={6}>
                <Card size="small" bordered={false} style={{ borderRadius: '8px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>TỔNG DOANH THU</Text>
                <Title level={3} style={{ margin: '8px 0', color: '#1890ff' }}>đ 12.4B</Title>
                <Text type="success" style={{ fontSize: '12px' }}><ArrowUpOutlined /> 8.2% vs last period</Text>
                </Card>
            </Col>

            <Col xs={24} sm={12} lg={6}>
                <Card size="small" bordered={false} style={{ borderRadius: '8px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>TỶ LỆ LẤP ĐẦY</Text>
                <Title level={3} style={{ margin: '8px 0', color: '#1890ff' }}>94%</Title>
                <Text type="secondary" style={{ fontSize: '12px' }}>Stable</Text>
                </Card>
            </Col>

            <Col xs={24} sm={12} lg={6}>
                <Card size="small" bordered={false} style={{ borderRadius: '8px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>LƯỢT KHÁCH</Text>
                <Title level={3} style={{ margin: '8px 0', color: '#1890ff' }}>45,210</Title>
                <Text type="success" style={{ fontSize: '12px' }}><ArrowUpOutlined /> 2.4% vs last period</Text>
                </Card>
            </Col>

            <Col xs={24} sm={12} lg={6}>
                <Card size="small" bordered={false} style={{ borderRadius: '8px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>YÊU CẦU BẢO TRÌ</Text>
                <Title level={3} style={{ margin: '8px 0', color: '#cf1322' }}>12</Title>
                <Text type="danger" style={{ fontSize: '12px' }}>Pending action</Text>
                </Card>
            </Col>

          </Row>

          {/* Table Section */}
          <Card 
            title="Hợp đồng sắp hết hạn" 
            extra={<Button type="link">VIEW ALL</Button>}
            bordered={false} 
            style={{ borderRadius: '8px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}
            bodyStyle={{ padding: 0 }}
          >
            <Table 
              columns={tableColumns} 
              dataSource={tableData} 
              pagination={false}
              scroll={{ x: 600 }}
            />
          </Card>

        </Content>
      </Layout>
    </Layout>
  );
}