import React, { useState } from 'react';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import { Layout, Menu, Avatar, Badge, Typography, Button, Drawer, Grid } from 'antd';
import { 
  DashboardOutlined, 
  ShopOutlined, 
  FileTextOutlined, 
  DollarOutlined, 
  ToolOutlined, 
  LogoutOutlined, 
  BellOutlined, 
  MenuOutlined,
  UserOutlined
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;
const { useBreakpoint } = Grid;

export default function StaffLayout() {
  const navigate = useNavigate();
  const location = useLocation();
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

  // 🌟 Staff-Specific Menu Items 
  // (In the future, we will filter this array based on if they are KD-TC or VH-BT!)
  const menuItems = [
    { key: '/staff', icon: <DashboardOutlined />, label: 'Bàn làm việc', onClick: () => handleMenuClick("/staff") },
    { key: '/staff/premises', icon: <ShopOutlined />, label: 'Quản lý Mặt bằng', onClick: () => handleMenuClick("/staff/premises") },
    { key: '/staff/contracts', icon: <FileTextOutlined />, label: 'Quản lý Hợp đồng', onClick: () => handleMenuClick("/staff/contracts") },
    { key: '/staff/finance', icon: <DollarOutlined />, label: 'Tài chính - Công nợ', onClick: () => handleMenuClick("/staff/finance") },
    { key: '/staff/maintenance', icon: <ToolOutlined />, label: 'Vận hành - Bảo trì', onClick: () => handleMenuClick("/staff/maintenance") },
  ];

  const sidebarContent = (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: '#fff' }}>
      <div style={{ padding: '24px 20px', borderBottom: '1px solid #f0f0f0' }}>
        <Title level={4} style={{ margin: 0, color: '#1890ff' }}>Vận hành trung tâm</Title>
        <Text type="secondary" style={{ fontSize: '12px' }}>Không gian nhân viên</Text>
      </div>
      
      <Menu
        mode="inline"
        selectedKeys={[location.pathname.startsWith('/staff/finance') ? '/staff/finance' : location.pathname]}
        items={menuItems}
        style={{ borderRight: 0, flex: 1, padding: '16px 0' }}
      />
      <Menu mode="inline" selectable={false} items={[{ key: 'logout', icon: <LogoutOutlined />, label: 'Đăng xuất', onClick: handleLogout }]} style={{ borderTop: '1px solid #f0f0f0', padding: '16px 0' }} />
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
            {/* Contextual Greeting */}
            <Title level={5} style={{ margin: 0 }}>Nguyễn Văn A — Nhân viên KD-TC</Title>
          </div>

          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            {/* Staff might get tasks assigned to them, so notifications are critical */}
            <Badge count={5}><BellOutlined style={{ fontSize: '18px', cursor: 'pointer' }} /></Badge>
            <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff', cursor: 'pointer' }} />
          </div>
        </Header>

        <Content style={{ margin: '24px 32px', overflow: 'initial' }}>
          <Outlet /> 
        </Content>
      </Layout>
    </Layout>
  );
}