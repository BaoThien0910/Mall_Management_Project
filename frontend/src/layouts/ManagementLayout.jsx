import React, { useState } from 'react';
import { useNavigate, Outlet } from 'react-router-dom';
import { Layout, Menu, Avatar, Badge, Typography, Button, Drawer, Grid } from 'antd';
import { 
  BarChartOutlined, 
  CheckCircleOutlined, 
  FileDoneOutlined, 
  NotificationOutlined, 
  LogoutOutlined, 
  BellOutlined, 
  MenuOutlined,
  CrownOutlined
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;
const { useBreakpoint } = Grid;

export default function ManagementLayout() {
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

  // 🌟 Management-Specific Menu Items 
  const menuItems = [
    { key: '/management', icon: <BarChartOutlined />, label: 'Tổng quan', onClick: () => handleMenuClick("/management") },
    { key: '/management/approvals', icon: <CheckCircleOutlined />, label: 'Duyệt yêu cầu', onClick: () => handleMenuClick("/management/approvals") },
    { key: '/management/reports', icon: <FileDoneOutlined />, label: 'Báo cáo tổng hợp', onClick: () => handleMenuClick("/management/reports") },
    { key: '/management/announcements', icon: <NotificationOutlined />, label: 'Ban hành Thông báo', onClick: () => handleMenuClick("/management/announcements") },
  ];

  const sidebarContent = (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: '#fff' }}>
      <div style={{ padding: '24px 20px', borderBottom: '1px solid #f0f0f0' }}>
        <Title level={4} style={{ margin: 0, color: '#722ed1' }}>Ban quản lý</Title>
        <Text type="secondary" style={{ fontSize: '12px' }}>Hội đồng quản trị</Text>
      </div>
      
      <Menu mode="inline" defaultSelectedKeys={['/management']} items={menuItems} style={{ borderRight: 0, flex: 1, padding: '16px 0' }} />
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
            <Title level={5} style={{ margin: 0 }}>Ban Quản Lý</Title>
          </div>

          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <Badge count={8}><BellOutlined style={{ fontSize: '18px', cursor: 'pointer' }} /></Badge>
            <Avatar icon={<CrownOutlined />} style={{ backgroundColor: '#722ed1', cursor: 'pointer' }} />
          </div>
        </Header>

        <Content style={{ margin: '24px 32px', overflow: 'initial' }}>
          <Outlet /> 
        </Content>
      </Layout>
    </Layout>
  );
}