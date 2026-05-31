import { Breadcrumb, Button, Space, Typography } from "antd";
import { HomeOutlined } from "@ant-design/icons";

const { Title, Text } = Typography;

export default function PageHeader({ title, subtitle, breadcrumb = [], actionText, actionIcon, onAction, actionDisabled, extra }) {
  return (
    <div className="page-header-block">
      <div>
        <Breadcrumb
          className="app-breadcrumb"
          items={[
            { title: <><HomeOutlined /> Trang chủ</> },
            ...breadcrumb.map((item) => ({ title: item })),
          ]}
        />
        <Title level={2} className="page-title">{title}</Title>
        {subtitle ? <Text type="secondary">{subtitle}</Text> : null}
      </div>
      <Space wrap>
        {extra}
        {actionText ? (
          <Button type="primary" icon={actionIcon} onClick={onAction} disabled={actionDisabled}>{actionText}</Button>
        ) : null}
      </Space>
    </div>
  );
}
