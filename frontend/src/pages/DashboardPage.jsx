import React from 'react';
import { Card, Table, Typography, Row, Col, Button, Tag } from 'antd';
import { ArrowUpOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export default function DashboardPage() {
  const tableColumns = [
    {
      title: 'Khách thuê',
      dataIndex: 'tenant',
      key: 'tenant',
      render: (text, record) => (
        <div>
          <Text strong>{text}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {record.category}
          </Text>
        </div>
      ),
    },
    { title: 'Mặt bằng', dataIndex: 'unit', key: 'unit' },
    { title: 'Ngày hết hạn', dataIndex: 'date', key: 'date' },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      render: (s) => (
        <Tag color={s === 'KHẨN CẤP' ? 'red' : 'volcano'}>{s}</Tag>
      ),
    },
    {
      title: 'Thao tác',
      key: 'action',
      render: () => <Button size="small">Gia hạn</Button>,
      align: 'right',
    },
  ];

  const tableData = [
    {
      key: '1',
      tenant: 'Starbucks',
      category: 'Ẩm thực',
      unit: 'GF-01',
      date: '15/10/2023',
      status: 'KHẨN CẤP',
    },
    {
      key: '2',
      tenant: 'H&M',
      category: 'Thời trang',
      unit: 'L1-12',
      date: '02/11/2023',
      status: 'CẢNH BÁO',
    },
  ];

  return (
    <>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-end',
          marginBottom: '24px',
        }}
      >
        <div>
          <Title level={2} style={{ margin: 0 }}>
            Chào buổi sáng, Quản trị viên
          </Title>
          <Text type="secondary">Tình hình hoạt động trung tâm hôm nay.</Text>
        </div>
        <Button>7 ngày qua</Button>
      </div>

      <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" style={{ borderRadius: '8px' }}>
            <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>
              TỔNG DOANH THU
            </Text>
            <Title level={3} style={{ margin: '8px 0', color: '#1890ff' }}>
              12,4 tỷ ₫
            </Title>
            <Text type="success" style={{ fontSize: '12px' }}>
              <ArrowUpOutlined /> +8,2% so với kỳ trước
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" style={{ borderRadius: '8px' }}>
            <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>
              TỶ LỆ LẤP ĐẦY
            </Text>
            <Title level={3} style={{ margin: '8px 0', color: '#1890ff' }}>
              94%
            </Title>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              Ổn định
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" style={{ borderRadius: '8px' }}>
            <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>
              LƯỢT KHÁCH
            </Text>
            <Title level={3} style={{ margin: '8px 0', color: '#1890ff' }}>
              45.210
            </Title>
            <Text type="success" style={{ fontSize: '12px' }}>
              <ArrowUpOutlined /> +2,4% so với kỳ trước
            </Text>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card size="small" style={{ borderRadius: '8px' }}>
            <Text type="secondary" style={{ fontSize: '12px', fontWeight: 'bold' }}>
              YÊU CẦU BẢO TRÌ
            </Text>
            <Title level={3} style={{ margin: '8px 0', color: '#cf1322' }}>
              12
            </Title>
            <Text type="danger" style={{ fontSize: '12px' }}>
              Đang chờ xử lý
            </Text>
          </Card>
        </Col>
      </Row>

      <Card
        title="Hợp đồng sắp hết hạn"
        extra={<Button type="link">Xem tất cả</Button>}
        bordered={false}
        styles={{ body: { padding: 0 } }}
        style={{ borderRadius: '8px' }}
      >
        <Table
          columns={tableColumns}
          dataSource={tableData}
          pagination={false}
          scroll={{ x: 600 }}
        />
      </Card>
    </>
  );
}
