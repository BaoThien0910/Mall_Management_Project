import { Tag } from "antd";
import { statusColor } from "../../utils/data";

export default function StatusTag({ value }) {
  if (!value) return <Tag>-</Tag>;
  return <Tag color={statusColor(value)}>{value}</Tag>;
}
