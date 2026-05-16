import React, { useState } from 'react';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { Layout, Menu, Avatar, Badge, Typography, Button, Drawer, Grid } from 'antd';
import {
  HomeOutlined,
  FileTextOutlined,
  CreditCardOutlined,
  ToolOutlined,
  LogoutOutlined,
  BellOutlined,
  MenuOutlined,
} from '@ant-design/icons';

import AppBreadcrumb from '../components/layout/AppBreadcrumb';
import { logout } from '../store/authSlice';
import { clearCodes } from '../store/permissionSlice';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;
const { useBreakpoint } = Grid;

function tenantMenuKey(pathname) {
  if (pathname.startsWith('/tenant/billing')) return '/tenant/billing';
  return pathname;
}

export default function TenantLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const screens = useBreakpoint();
  const isMobile = screens.lg === false;
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleLogout = () => {
    dispatch(logout());
    dispatch(clearCodes());
    navigate('/login');
  };

  const handleMenuClick = (path) => {
    navigate(path);
    if (isMobile) setDrawerOpen(false);
  };

  const menuItems = [
    { key: '/tenant', icon: <HomeOutlined />, label: 'Trang chủ', onClick: () => handleMenuClick('/tenant') },
    { key: '/tenant/contract', icon: <FileTextOutlined />, label: 'Hợp đồng của tôi', onClick: () => handleMenuClick('/tenant/contract') },
    { key: '/tenant/billing', icon: <CreditCardOutlined />, label: 'Công nợ & Thanh toán', onClick: () => handleMenuClick('/tenant/billing') },
    { key: '/tenant/maintenance', icon: <ToolOutlined />, label: 'Yêu cầu sửa chữa', onClick: () => handleMenuClick('/tenant/maintenance') },
  ];

  const sidebarContent = (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: '#fff' }}>
      <div style={{ padding: '24px 20px', borderBottom: '1px solid #f0f0f0' }}>
        <Title level={4} style={{ margin: 0, color: '#af6715' }}>
          Cổng khách thuê
        </Title>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          Trung tâm Main Plaza
        </Text>
      </div>

      <Menu
        mode="inline"
        selectedKeys={[tenantMenuKey(location.pathname)]}
        items={menuItems}
        style={{ borderRight: 0, flex: 1, padding: '16px 0' }}
      />
      <Menu
        mode="inline"
        selectable={false}
        items={[{ key: 'logout', icon: <LogoutOutlined />, label: 'Đăng xuất', onClick: handleLogout }]}
        style={{ borderTop: '1px solid #f0f0f0', padding: '16px 0' }}
      />
    </div>
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {!isMobile && (
        <Sider
          width={250}
          theme="light"
          style={{ borderRight: '1px solid #f0f0f0', height: '100vh', position: 'sticky', top: 0 }}
        >
          {sidebarContent}
        </Sider>
      )}

      <Drawer title={null} placement="left" closable={false} onClose={() => setDrawerOpen(false)} open={drawerOpen} bodyStyle={{ padding: 0 }} width={260}>
        {sidebarContent}
      </Drawer>

      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {isMobile && (
              <Button
                type="text"
                icon={<MenuOutlined />}
                onClick={() => setDrawerOpen(true)}
                style={{ fontSize: '18px', width: 48, height: 48, marginLeft: -16 }}
              />
            )}
            <Title level={5} style={{ margin: 0 }}>
              Xin chào, Starbucks — GF-01
            </Title>
          </div>

          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <Badge count={2}>
              <BellOutlined style={{ fontSize: '18px', cursor: 'pointer' }} />
            </Badge>
            <Avatar style={{ backgroundColor: '#52c41a', cursor: 'pointer' }}>S</Avatar>
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
