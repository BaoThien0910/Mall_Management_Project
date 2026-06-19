import { Card, Typography } from "antd";
const { Text, Title } = Typography;
export default function StatCard({ label, value, hint, danger }) {
  return (
    <Card className="stat-card" bordered={false}>
      <Text type="secondary" className="stat-label">{label}</Text>
      <Title level={3} className={danger ? "stat-value stat-danger" : "stat-value"}>{value}</Title>
      {hint ? <Text className={danger ? "stat-hint stat-danger" : "stat-hint"}>{hint}</Text> : null}
    </Card>
  );
}
