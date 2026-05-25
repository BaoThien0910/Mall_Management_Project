import { createElement, useEffect, useMemo, useState } from "react";
import {
  Avatar,
  Badge,
  Button,
  Drawer,
  Grid,
  Input,
  Layout,
  Menu,
  Space,
  Typography,
} from "antd";
import {
  LogoutOutlined,
  MenuOutlined,
  SearchOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { menuItems } from "../constants/routes";
import { ROLE, ROLE_LABEL } from "../constants/roles";
import { dashboardService } from "../services/dashboardService";
import { useAuth } from "../hooks/useAuth";

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

function getPortalTitle(role) {
  if (role === ROLE.KHACH_THUE) return "Cổng khách thuê";
  if (role === ROLE.QTV) return "Quản trị hệ thống";
  if (role === ROLE.BQL) return "Ban Quản Lý";
  if (role === ROLE.TP_KDTC || role === ROLE.NV_KDTC) return "Kinh doanh - Tài chính";
  if (role === ROLE.TP_VHBT || role === ROLE.NV_VHBT) return "Vận hành - Bảo trì";
  return "Quản lý TTTM";
}

function getUserName(user, role) {
  return (
    user?.ten_dang_nhap ||
    user?.tendangnhap ||
    user?.ho_ten ||
    user?.hoten ||
    ROLE_LABEL[role] ||
    "Người dùng"
  );
}

function getMenuBadgeValue(menuBadges, badgeKey) {
  if (!badgeKey || !menuBadges) return 0;

  const numberValue = Number(menuBadges[badgeKey]);

  if (Number.isNaN(numberValue) || numberValue <= 0) return 0;

  return numberValue;
}

export default function AppShell() {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const screens = Grid.useBreakpoint();
  const isMobile = !screens.md;
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [menuBadges, setMenuBadges] = useState({});

  useEffect(() => {
    let ignore = false;

    async function loadBadges() {
      try {
        const data = await dashboardService.getMyDashboard();

        if (!ignore) {
          setMenuBadges(data?.menu_badges || {});
        }
      } catch {
        if (!ignore) {
          setMenuBadges({});
        }
      }
    }

    if (role) loadBadges();
    else setMenuBadges({});

    return () => {
      ignore = true;
    };
  }, [role, location.pathname]);

  const allowedMenu = useMemo(
    () => menuItems.filter((item) => item.allowedRoles.includes(role)),
    [role],
  );

  const selectedKey =
    allowedMenu.find(
      (item) =>
        location.pathname === item.key ||
        (item.key !== "/" && location.pathname.startsWith(item.key)),
    )?.key || "/";

  const menu = (
    <div className="sidebar-inner">
      <div className="brand-box">
        <div className={role === ROLE.KHACH_THUE ? "brand-title tenant" : "brand-title"}>
          {getPortalTitle(role)}
        </div>
        <div className="brand-subtitle">Trung tâm Main Plaza</div>
      </div>

      <Menu
        mode="inline"
        selectedKeys={[selectedKey]}
        items={allowedMenu.map(({ key, label, icon, badgeKey }) => {
          const badgeValue = getMenuBadgeValue(menuBadges, badgeKey);

          return {
            key,
            icon: icon ? createElement(icon) : null,
            label: (
              <span className="menu-label-with-badge">
                <span>{label}</span>
                {badgeValue > 0 ? (
                  <Badge
                    count={badgeValue}
                    size="small"
                    overflowCount={99}
                    className="menu-count-badge"
                  />
                ) : null}
              </span>
            ),
          };
        })}
        onClick={({ key }) => {
          navigate(key);
          setDrawerOpen(false);
        }}
        className="side-menu"
      />

      <div className="logout-box">
        <Button icon={<LogoutOutlined />} type="text" block onClick={logout} className="logout-button">
          Đăng xuất
        </Button>
      </div>
    </div>
  );

  return (
    <Layout className="app-layout">
      {!isMobile ? (
        <Sider width={222} theme="light" className="app-sider">
          {menu}
        </Sider>
      ) : null}

      <Layout>
        <Header className="app-header">
          <Space size={12} className="header-left">
            {isMobile ? <Button icon={<MenuOutlined />} onClick={() => setDrawerOpen(true)} /> : null}
            <Input className="header-search" prefix={<SearchOutlined />} placeholder="Tìm kiếm..." />
          </Space>

          <Space size={18}>
            {!isMobile ? <Text strong>Xin chào, {getUserName(user, role)}</Text> : null}
            <Avatar className="app-avatar" icon={<UserOutlined />}>
              {String(getUserName(user, role)).charAt(0).toUpperCase()}
            </Avatar>
          </Space>
        </Header>

        <Content className="app-content">
          <Outlet context={{ menuBadges }} />
        </Content>
      </Layout>

      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        placement="left"
        width={286}
        styles={{ body: { padding: 0 } }}
      >
        {menu}
      </Drawer>
    </Layout>
  );
}
