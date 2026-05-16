// src/layouts/AdminLayout.jsx
import React, { useState } from 'react';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { Layout, Menu, Input, Avatar, Badge, Typography, Button, Drawer, Grid } from 'antd';
import { 
  DashboardOutlined,  
  LogoutOutlined, 
  BellOutlined, 
  SearchOutlined, 
  MenuOutlined, 
  TeamOutlined, 
  HistoryOutlined
} from '@ant-design/icons';

import AppBreadcrumb from '../components/layout/AppBreadcrumb';
import { logout } from '../store/authSlice';
import { clearCodes } from '../store/permissionSlice';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;
const { useBreakpoint } = Grid; // 🌟 This reads the exact screen size!

export default function AdminLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const screens = useBreakpoint();
  
  // If the screen is smaller than 'lg' (Large/Desktop), we consider it mobile
  const isMobile = screens.lg === false; 
  
  // Controls whether the mobile drawer is open or closed
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleLogout = () => {
    dispatch(logout());
    dispatch(clearCodes());
    navigate('/login');
  };

  const handleMenuClick = (path) => {
    navigate(path);
    if (isMobile) {
      setDrawerOpen(false); // Close the beautiful drawer after clicking
    }
  };

  const menuItems = [
    { key: '/admin', icon: <DashboardOutlined />, label: 'Bảng điều khiển', onClick: () => handleMenuClick("/admin") },
    
    { key: '/admin/accounts', icon: <TeamOutlined />, label: 'Quản lý Tài khoản', onClick: () => handleMenuClick("/admin/accounts") },
    { key: '/admin/logs', icon: <HistoryOutlined />, label: 'Nhật ký thao tác', onClick: () => handleMenuClick("/admin/logs") },
  ];

  // 🌟 We extract the menu content into a variable so we can reuse it 
  // in both the Desktop Sidebar and the Mobile Drawer without typing it twice!
  const sidebarContent = (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: '#fff' }}>
      <div style={{ padding: '24px 20px', borderBottom: '1px solid #f0f0f0' }}>
        <Title level={4} style={{ margin: 0, color: '#1890ff' }}>Quản trị hệ thống</Title>
      </div>
      
      <Menu mode="inline" selectedKeys={[location.pathname]} items={menuItems} style={{ borderRight: 0, flex: 1, padding: '16px 0' }} />
      <Menu mode="inline" selectable={false} items={[{ key: 'logout', icon: <LogoutOutlined />, label: 'Đăng xuất', onClick: handleLogout }]} style={{ borderTop: '1px solid #f0f0f0', padding: '16px 0' }} />
    </div>
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      
      {/* ─── DESKTOP SIDEBAR (Hides completely on Mobile) ─── */}
      {!isMobile && (
        <Sider width={250} theme="light" style={{ borderRight: '1px solid #f0f0f0', height: '100vh', position: 'sticky', top: 0 }}>
          {sidebarContent}
        </Sider>
      )}

      {/* ─── MOBILE DRAWER (Only active on Mobile) ─── */}
      <Drawer
        title={null}
        placement="left"
        closable={false}
        onClose={() => setDrawerOpen(false)}
        open={drawerOpen}
        bodyStyle={{ padding: 0 }}
        width={260}
      >
        {sidebarContent}
      </Drawer>

      {/* ─── MAIN CONTENT AREA ─── */}
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #f0f0f0' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {/* Show the Hamburger Button ONLY on mobile */}
            {isMobile && (
              <Button 
                type="text" 
                icon={<MenuOutlined />} 
                onClick={() => setDrawerOpen(true)} 
                style={{ fontSize: '18px', width: 48, height: 48, marginLeft: -16 }} 
              />
            )}
            <Input prefix={<SearchOutlined style={{color: '#bfbfbf'}}/>} placeholder="Tìm kiếm..." style={{ width: isMobile ? 150 : 300, borderRadius: '20px' }} />
          </div>

          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <Badge dot><BellOutlined style={{ fontSize: '18px', cursor: 'pointer' }} /></Badge>
            <Avatar style={{ backgroundColor: '#1890ff', cursor: 'pointer' }}>A</Avatar>
          </div>
        </Header>

        <Content style={{ margin: isMobile ? '16px 12px 24px' : '24px 32px', overflow: 'initial' }}>
          <AppBreadcrumb />
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}