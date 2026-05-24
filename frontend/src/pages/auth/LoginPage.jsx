import { ArrowRightOutlined, LockOutlined, MailOutlined } from "@ant-design/icons";
import { Button, Checkbox, Form, Input, Typography, message } from "antd";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { login } from "../../store/authSlice";
import { showApiError } from "../../services/apiClient";

const { Title, Text } = Typography;

export default function LoginPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const loading = useSelector((state) => state.auth.loading);

  const onFinish = async (values) => {
    try {
      await dispatch(login(values)).unwrap();
      message.success("Đăng nhập thành công!");
      navigate("/", { replace: true });
    } catch (error) {
      showApiError(error);
    }
  };

  return (
    <div className="login-page">
      <div className="login-panel">
        <div className="login-form-wrap">
          <Title level={2} className="login-title">Quản lý TTTM</Title>
          <Text type="secondary" className="login-subtitle">Hệ thống quản lý trung tâm thương mại</Text>
          <Form layout="vertical" onFinish={onFinish} className="login-form" initialValues={{ remember: true }}>
            <Form.Item label="Email / Tài khoản" name="ten_dang_nhap" rules={[{ required: true, message: "Vui lòng nhập tài khoản!" }]}>
              <Input size="large" prefix={<MailOutlined />} placeholder="qtv_admin" />
            </Form.Item>
            <Form.Item label="Mật khẩu" name="mat_khau" rules={[{ required: true, message: "Vui lòng nhập mật khẩu!" }]}>
              <Input.Password size="large" prefix={<LockOutlined />} placeholder="Admin12345" />
            </Form.Item>
            <Form.Item name="remember" valuePropName="checked"><Checkbox>Ghi nhớ đăng nhập</Checkbox></Form.Item>
            <Button type="primary" size="large" block htmlType="submit" loading={loading} icon={<ArrowRightOutlined />} className="login-button">Đăng nhập</Button>
          </Form>
        </div>
      </div>
      <div className="login-hero">
        <div className="system-status">● Trạng thái hệ thống: Ổn định</div>
      </div>
    </div>
  );
}
