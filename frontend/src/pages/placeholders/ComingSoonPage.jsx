import React from 'react';
import { Card, Empty, Typography } from 'antd';

const { Title, Paragraph } = Typography;

/** Trang chờ chức năng đang được xây dựng */

export default function ComingSoonPage({ title, description }) {
  return (
    <Card bordered={false} style={{ borderRadius: 8 }}>
      <Title level={4} style={{ marginTop: 0 }}>
        {title}
      </Title>
      <Paragraph type="secondary">{description}</Paragraph>
      <Empty description="Nội dung sẽ có sau khi nối API / giao diện chi tiết" />
    </Card>
  );
}
