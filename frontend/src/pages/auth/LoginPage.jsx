import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { Form, Input, Button, Checkbox, Typography, Row, Col, message } from 'antd';
import { MailOutlined, LockOutlined, ArrowRightOutlined, CheckCircleFilled } from '@ant-design/icons';
import { loginAPI } from '../../services/authService';
import { setCredentials } from '../../store/authSlice';
import { setCodes } from '../../store/permissionSlice';

// Import your background image! (Adjust the path if yours is named differently)
import mallBg from '../../assets/mall-bg.jpg'; 

const { Title, Text } = Typography;

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const onFinish = async (values) => {
    setLoading(true);
    
    // Ensure 'remember' is always sent, even if unchecked
    const payload = {
      ...values,
      remember: values.remember || false
    };

    try {
      const data = await loginAPI(payload); 
      
      // 1. SECURE STORAGE: Save to session memory instead of local storage
      dispatch(
        setCredentials({
          token: data.token,
          role: data.role,
          email: data.email ?? values.email,
        })
      );
      dispatch(setCodes(data.permissions ?? []));

      message.success('Đăng nhập thành công!');

      if (data.role === 'admin') {
        navigate("/admin");
      } else if (data.role === "tenant") {
        navigate("/tenant");
      } else if (data.role === "staff") {
        navigate("/staff");
      } else if (data.role === "management") {
        navigate("/management");
      } else {
        message.error("Lỗi: Không nhận diện được vai trò!");
      }

    } catch (error) {
      if (error.response) {
        message.error("Lỗi: " + error.response.data.detail);
      } else {
        message.error("Không thể kết nối đến máy chủ.");
        console.error(error);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Row style={{ minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      
      {/* ─── LEFT SIDE: FORM ─── */}
      <Col xs={24} lg={12} style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#ffffff', padding: '48px', zIndex: 1, boxShadow: '2px 0 8px rgba(0,0,0,0.05)' }}>
        <div style={{ width: '100%', maxWidth: '400px' }}>
          <div style={{ marginBottom: '40px', textAlign: 'center' }}>
            <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>Quản lý TTTM</Title>
            <Text type="secondary" style={{ fontSize: '16px' }}>Hệ thống quản lý trung tâm thương mại</Text>
          </div>

          <Form  
            name="login_form" 
            layout="vertical" 
            onFinish={onFinish} 
            size="large"
          >
            <Form.Item label={<Text strong>Email / Tài khoản</Text>} name="email" rules={[{ required: true, message: 'Vui lòng nhập email!' }]}>
              <Input prefix={<MailOutlined style={{ color: '#bfbfbf' }} />} placeholder="admin@mainplaza.com" />
            </Form.Item>

            <Form.Item label={<Text strong>Mật khẩu</Text>} name="password" rules={[{ required: true, message: 'Vui lòng nhập mật khẩu!' }]}>
              <Input.Password prefix={<LockOutlined style={{ color: '#bfbfbf' }} />} placeholder="••••••••" />
            </Form.Item>

            <Form.Item name="remember" valuePropName="checked" style={{ marginBottom: '24px' }}>
              <Checkbox>Ghi nhớ đăng nhập</Checkbox>
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading} icon={<ArrowRightOutlined />}>Đăng nhập</Button>
            </Form.Item>
          </Form> 
        </div>
      </Col>

      {/* ─── RIGHT SIDE: IMAGE ─── */}
      <Col xs={0} lg={12} style={{ position: 'relative', overflow: 'hidden', backgroundColor: '#e6f7ff' }}>
        <img src={mallBg} alt="Trung tâm thương mại" style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', inset: 0 }} />
        <div style={{ position: 'absolute', inset: 0, backgroundColor: 'rgba(24, 144, 255, 0.1)', mixBlendMode: 'multiply' }}></div>
        <div style={{ position: 'absolute', bottom: '40px', right: '40px', backgroundColor: 'rgba(255, 255, 255, 0.9)', backdropFilter: 'blur(10px)', padding: '16px 24px', borderRadius: '8px' }}>
          <Text strong><CheckCircleFilled style={{ color: '#52c41a' }} /> Trạng thái hệ thống: Ổn định</Text>
        </div>
      </Col>

    </Row>
  );
}