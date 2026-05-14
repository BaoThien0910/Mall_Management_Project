import React, { useState } from 'react';
import { Form, Input, Button, Checkbox, Typography, Row, Col, message } from 'antd';
import { MailOutlined, LockOutlined, ArrowRightOutlined, CheckCircleFilled } from '@ant-design/icons';

const { Title, Text } = Typography;

export default function LoginPage({ onLogin }) {
  const [loading, setLoading] = useState(false);

  // Ant Design automatically handles preventing the default form submission 
  // and extracts the values for us!
  const onFinish = async (values) => {
    setLoading(true);
    // Pass the extracted values (email, password, remember) up to your App.jsx
    if (onLogin) {
      await onLogin(values);
    }
    setLoading(false);
  };

  return (
    <Row style={{ minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      
      {/* ─── LEFT SIDE: FORM ─── */}
      <Col xs={24} lg={12} style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#ffffff', padding: '48px', zIndex: 1, boxShadow: '2px 0 8px rgba(0,0,0,0.05)' }}>
        <div style={{ width: '100%', maxWidth: '400px' }}>
          
          {/* Brand Header */}
          <div style={{ marginBottom: '40px', textAlign: 'center' }}>
            <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>MallAdmin Pro</Title>
            <Text type="secondary" style={{ fontSize: '16px' }}>Enter your administrative credentials.</Text>
          </div>

          {/* Ant Design Form */}
          <Form
            name="login_form"
            layout="vertical"
            initialValues={{ remember: false }}
            onFinish={onFinish}
            size="large"
          >
            <Form.Item
              label={<Text strong>Email Address</Text>}
              name="email"
              rules={[{ required: true, message: 'Please input your email!' }, { type: 'email', message: 'Please enter a valid email!' }]}
            >
              <Input prefix={<MailOutlined style={{ color: '#bfbfbf' }} />} placeholder="admin@mainplaza.com" />
            </Form.Item>

            <Form.Item
              label={
                <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                  <Text strong>Password</Text>
                </div>
              }
              name="password"
              rules={[{ required: true, message: 'Please input your password!' }]}
            >
              <Input.Password prefix={<LockOutlined style={{ color: '#bfbfbf' }} />} placeholder="••••••••" />
            </Form.Item>

            <Form.Item name="remember" valuePropName="checked" style={{ marginBottom: '24px' }}>
              <Checkbox>Remember Me</Checkbox>
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading} icon={<ArrowRightOutlined />} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'row-reverse', gap: '8px' }}>
                Sign In
              </Button>
            </Form.Item>
          </Form>

          {/* Footer */}
          <div style={{ marginTop: '32px', textAlign: 'center', borderTop: '1px solid #f0f0f0', paddingTop: '24px' }}>
            <Text type="secondary">Need assistance? <a href="#">Contact Support</a>.</Text>
          </div>

        </div>
      </Col>

      {/* ─── RIGHT SIDE: IMAGE ─── */}
      <Col xs={0} lg={12} style={{ position: 'relative', overflow: 'hidden', backgroundColor: '#e6f7ff' }}>
        <img 
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuBFXXtOc-Jvdb939ybodSZ6rGU5bMjWbAwGOKuEx1k1SfZu9YwURnFL3IurzpQHNRganl9EHho2dcPu0YGADsB-iteYuZI5ZqEfStEuCSlII6powuMInlNCL5A7MgRJrtW6erWoW6sPUEKeSFI9NS9ixYTvuLcSZGAhq72Sa6Chwhq-u40ElED-u9hD1GY9r5XlNoMPtIkPKx2J7Ay3gwuBqfo03I_kQg55F-UTlRaNVBSak2jUeQfmOT6LRgnF6_7GJdEaVEbDl1Gj" 
          alt="Modern Mall Interior" 
          style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', inset: 0 }}
        />
        
        {/* Subtle Blue Overlay */}
        <div style={{ position: 'absolute', inset: 0, backgroundColor: 'rgba(24, 144, 255, 0.1)', mixBlendMode: 'multiply' }}></div>
        
        {/* Floating Status Card */}
        <div style={{ position: 'absolute', bottom: '40px', right: '40px', backgroundColor: 'rgba(255, 255, 255, 0.9)', backdropFilter: 'blur(10px)', padding: '16px 24px', borderRadius: '8px', boxShadow: '0 8px 16px rgba(0,0,0,0.1)', maxWidth: '300px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <CheckCircleFilled style={{ color: '#52c41a', fontSize: '18px' }} />
            <Text strong>System Status: Optimal</Text>
          </div>
          <Text type="secondary" style={{ fontSize: '12px' }}>All core management nodes are online and securely connected to the AntD framework.</Text>
        </div>
      </Col>

    </Row>
  );
}