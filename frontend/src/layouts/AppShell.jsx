import { cloneElement, createElement, useEffect, useMemo, useState } from "react";
import {
  Avatar,
  Badge,
  Button,
  Divider,
  Drawer,
  Dropdown,
  Form,
  Grid,
  Input,
  Layout,
  Menu,
  Modal,
  Space,
  Typography,
  message,
} from "antd";
import {
  LockOutlined,
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
import { authService } from "../services/authService";
import { showApiError } from "../services/apiClient";

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
  const [isChangePasswordOpen, setIsChangePasswordOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [passwordForm] = Form.useForm();
  const [currentDateTime, setCurrentDateTime] = useState(new Date());

  const handleChangePassword = async (values) => {
    setSubmitting(true);
    try {
      await authService.changePassword({
        mat_khau_cu: values.mat_khau_cu,
        mat_khau_moi: values.mat_khau_moi,
        xac_nhan_mat_khau_moi: values.xac_nhan_mat_khau_moi,
      });
      message.success("Đổi mật khẩu thành công");
      passwordForm.resetFields();
      setIsChangePasswordOpen(false);
    } catch (error) {
      showApiError(error);
    } finally {
      setSubmitting(false);
    }
  };

  const avatarMenuItems = [
    {
      key: "change-password",
      label: (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", width: "100%" }}>
          <LockOutlined style={{ fontSize: "16px" }} />
          <span>Đổi mật khẩu</span>
        </div>
      ),
      onClick: () => setIsChangePasswordOpen(true),
    },
    {
      type: "divider",
    },
    {
      key: "logout",
      label: (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", width: "100%" }}>
          <LogoutOutlined style={{ fontSize: "16px" }} />
          <span>Đăng xuất</span>
        </div>
      ),
      danger: true,
      onClick: logout,
    },
  ];

  const renderDropdown = (menuContent) => (
    <div
      style={{
        backgroundColor: "#fff",
        borderRadius: "8px",
        boxShadow: "0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 3px 6px -4px rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05)",
        minWidth: "220px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          padding: "16px 16px 12px",
        }}
      >
        <Avatar
          className="app-avatar"
          style={{ width: "40px", height: "40px", lineHeight: "40px", fontSize: "18px" }}
          icon={<UserOutlined />}
        >
          {String(getUserName(user, role)).charAt(0).toUpperCase()}
        </Avatar>
        <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
          <Text strong style={{ fontSize: "15px", display: "block", lineHeight: "1.2" }}>
            {getUserName(user, role)}
          </Text>
          <div>
            <span
              style={{
                background: "#e6f4ff",
                color: "#1677ff",
                borderRadius: "4px",
                padding: "2px 8px",
                fontSize: "12px",
                fontWeight: "500",
                display: "inline-block",
              }}
            >
              {ROLE_LABEL[role] || "Thành viên"}
            </span>
          </div>
        </div>
      </div>
      <Divider style={{ margin: "4px 0" }} />
      {cloneElement(menuContent, {
        style: {
          boxShadow: "none",
          border: "none",
          background: "transparent",
          padding: "4px 0",
        },
      })}
    </div>
  );

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

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentDateTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

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
            <Space size={8} className="header-datetime" style={{ display: "flex", alignItems: "center" }}>
              <Text style={{ color: "#1677ff", fontWeight: 500 }}>
                {currentDateTime.toLocaleString("vi-VN", {
                  year: "numeric",
                  month: "2-digit",
                  day: "2-digit",
                })}
              </Text>
              <Divider type="vertical" style={{ margin: "0 4px", borderColor: "#d9d9d9" }} />
              <Text style={{ color: "#1677ff", fontWeight: 500 }}>
                {currentDateTime.toLocaleString("vi-VN", {
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                  hour12: false,
                })}
              </Text>
            </Space>
          </Space>

          <Space size={18}>
            {!isMobile ? <Text strong>Xin chào, {getUserName(user, role)}</Text> : null}
            <Dropdown
              menu={{ items: avatarMenuItems }}
              dropdownRender={renderDropdown}
              trigger={["click"]}
              placement="bottom"
            >
              <Avatar className="app-avatar" style={{ cursor: "pointer" }} icon={<UserOutlined />}>
                {String(getUserName(user, role)).charAt(0).toUpperCase()}
              </Avatar>
            </Dropdown>
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

      <Modal
        title="Đổi mật khẩu"
        open={isChangePasswordOpen}
        onCancel={() => {
          passwordForm.resetFields();
          setIsChangePasswordOpen(false);
        }}
        footer={null}
        destroyOnClose
      >
        <Form
          form={passwordForm}
          layout="vertical"
          onFinish={handleChangePassword}
          style={{ marginTop: 16 }}
        >
          <Form.Item
            name="mat_khau_cu"
            label="Mật khẩu hiện tại"
            rules={[{ required: true, message: "Vui lòng nhập mật khẩu hiện tại!" }]}
          >
            <Input.Password placeholder="Nhập mật khẩu hiện tại" />
          </Form.Item>

          <Form.Item
            name="mat_khau_moi"
            label="Mật khẩu mới"
            rules={[
              { required: true, message: "Vui lòng nhập mật khẩu mới!" },
              { min: 8, message: "Mật khẩu mới phải có tối thiểu 8 ký tự!" },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
                message: "Mật khẩu mới phải bao gồm ít nhất 1 chữ hoa, 1 chữ thường và 1 chữ số!",
              },
            ]}
          >
            <Input.Password placeholder="Nhập mật khẩu mới (tối thiểu 8 ký tự, có chữ hoa, thường và số)" />
          </Form.Item>

          <Form.Item
            name="xac_nhan_mat_khau_moi"
            label="Xác nhận mật khẩu mới"
            dependencies={["mat_khau_moi"]}
            rules={[
              { required: true, message: "Vui lòng xác nhận mật khẩu mới!" },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue("mat_khau_moi") === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error("Mật khẩu xác nhận không khớp!"));
                },
              }),
            ]}
          >
            <Input.Password placeholder="Xác nhận lại mật khẩu mới" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: "right" }}>
            <Space>
              <Button
                onClick={() => {
                  passwordForm.resetFields();
                  setIsChangePasswordOpen(false);
                }}
              >
                Hủy
              </Button>
              <Button type="primary" htmlType="submit" loading={submitting}>
                Xác nhận
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
}
