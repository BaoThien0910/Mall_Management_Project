import React, { useState } from 'react';
import { useNavigate, Outlet } from 'react-router-dom';
import { Layout, Menu, Avatar, Badge, Typography, Button, Drawer, Grid } from 'antd';
import { 
  HomeOutlined, 
  FileTextOutlined, 
  CreditCardOutlined, 
  ToolOutlined, 
  LogoutOutlined, 
  BellOutlined, 
  MenuOutlined 
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;
const { useBreakpoint } = Grid;

export default function TenantLayout() {
  const navigate = useNavigate();
  const screens = useBreakpoint();
  const isMobile = screens.lg === false; 
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleLogout = () => {
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("role"); 
    navigate("/login");
  };

  const handleMenuClick = (path) => {
    navigate(path);
    if (isMobile) setDrawerOpen(false);
  };

  // 🌟 Tenant-Specific Menu Items
  const menuItems = [
    { key: '/tenant', icon: <HomeOutlined />, label: 'My Space', onClick: () => handleMenuClick("/tenant") },
    { key: '/tenant/contract', icon: <FileTextOutlined />, label: 'My Lease', onClick: () => handleMenuClick("/tenant/contract") },
    { key: '/tenant/billing', icon: <CreditCardOutlined />, label: 'Billing & Payments', onClick: () => handleMenuClick("/tenant/billing") },
    { key: '/tenant/maintenance', icon: <ToolOutlined />, label: 'Request Repair', onClick: () => handleMenuClick("/tenant/maintenance") },
  ];

  const sidebarContent = (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: '#fff' }}>
      <div style={{ padding: '24px 20px', borderBottom: '1px solid #f0f0f0' }}>
        <Title level={4} style={{ margin: 0, color: '#af6715' }}>Tenant Portal</Title>
        <Text type="secondary" style={{ fontSize: '12px' }}>Main Plaza Mall</Text>
      </div>
      
      <Menu mode="inline" defaultSelectedKeys={['/tenant']} items={menuItems} style={{ borderRight: 0, flex: 1, padding: '16px 0' }} />
      <Menu mode="inline" selectable={false} items={[{ key: 'logout', icon: <LogoutOutlined />, label: 'Logout', onClick: handleLogout }]} style={{ borderTop: '1px solid #f0f0f0', padding: '16px 0' }} />
    </div>
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      
      {!isMobile && (
        <Sider width={250} theme="light" style={{ borderRight: '1px solid #f0f0f0', height: '100vh', position: 'sticky', top: 0 }}>
          {sidebarContent}
        </Sider>
      )}

      <Drawer title={null} placement="left" closable={false} onClose={() => setDrawerOpen(false)} open={drawerOpen} bodyStyle={{ padding: 0 }} width={260}>
        {sidebarContent}
      </Drawer>

      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #f0f0f0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {isMobile && (
              <Button type="text" icon={<MenuOutlined />} onClick={() => setDrawerOpen(true)} style={{ fontSize: '18px', width: 48, height: 48, marginLeft: -16 }} />
            )}
            {/* Removed the search bar for tenants to keep it simple! */}
            <Title level={5} style={{ margin: 0 }}>Welcome, Starbucks GF-01</Title>
          </div>

          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <Badge count={2}><BellOutlined style={{ fontSize: '18px', cursor: 'pointer' }} /></Badge>
            <Avatar style={{ backgroundColor: '#52c41a', cursor: 'pointer' }}>S</Avatar>
          </div>
        </Header>

        <Content style={{ margin: '24px 32px', overflow: 'initial' }}>
          <Outlet /> 
        </Content>
      </Layout>
    </Layout>
  );
}