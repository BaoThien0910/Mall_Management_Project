import React from 'react';
import { Card, Table, Typography, Row, Col, Button, Tag } from 'antd';
import { ArrowUpOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export default function DashboardPage() {
  const tableColumns = [
    { 
      title: 'Tenant', 
      dataIndex: 'tenant', 
      key: 'tenant', 
      render: (text, record) => (
        <div>
          <Text strong>{text}</Text><br/>
          <Text type="secondary" style={{fontSize:'12px'}}>{record.category}</Text>
        </div>
      ) 
    },
    { title: 'Unit', dataIndex: 'unit', key: 'unit' },
    { title: 'Expiry Date', dataIndex: 'date', key: 'date' },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status', 
      render: (s) => <Tag color={s === 'URGENT' ? 'red' : 'volcano'}>{s}</Tag> 
    },
    { 
      title: 'Action', 
      key: 'action', 
      render: () => <Button size="small">Renew</Button>, 
      align: 'right' 
    }
  ];

  const tableData = [
    { key: '1', tenant: 'Starbucks', category: 'F&B', unit: 'GF-01', date: 'Oct 15, 2023', status: 'URGENT' },
    { key: '2', tenant: 'H&M', category: 'Fashion', unit: 'L1-12', date: 'Nov 02, 2023', status: 'WARNING' },
  ];

  return (
    <>
      {/* ─── GREETING ─── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>Chào buổi sáng, Admin</Title>
          <Text type="secondary">Here is what's happening at your property today.</Text>
        </div>
        <Button>📅 7 ngày qua</Button>
      </div>

      {/* ─── KPI CARDS ─── */}
      <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" style={{ borderRadius: '8px' }}>
            <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>TỔNG DOANH THU</Text>
            <Title level={3} style={{ margin: '8px 0', color: '#1890ff' }}>đ 12.4B</Title>
            <Text type="success" style={{ fontSize: '12px' }}><ArrowUpOutlined /> 8.2% vs last period</Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" style={{ borderRadius: '8px' }}>
            <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>TỶ LỆ LẤP ĐẦY</Text>
            <Title level={3} style={{ margin: '8px 0', color: '#1890ff' }}>94%</Title>
            <Text type="secondary" style={{ fontSize: '12px' }}>Stable</Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" style={{ borderRadius: '8px' }}>
            <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>LƯỢT KHÁCH</Text>
            <Title level={3} style={{ margin: '8px 0', color: '#1890ff' }}>45,210</Title>
            <Text type="success" style={{ fontSize: '12px' }}><ArrowUpOutlined /> 2.4% vs last period</Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" style={{ borderRadius: '8px' }}>
            <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>YÊU CẦU BẢO TRÌ</Text>
            <Title level={3} style={{ margin: '8px 0', color: '#cf1322' }}>12</Title>
            <Text type="danger" style={{ fontSize: '12px' }}>Pending action</Text>
          </Card>
        </Col>
      </Row>

      {/* ─── TABLE ─── */}
      <Card title="Hợp đồng sắp hết hạn" extra={<Button type="link">VIEW ALL</Button>} bordered={false} bodyStyle={{ padding: 0 }} style={{ borderRadius: '8px' }}>
        <Table columns={tableColumns} dataSource={tableData} pagination={false} scroll={{ x: 600 }} />
      </Card>
    </>
  );
}