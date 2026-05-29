import { Button, Card, Input, Select, Space } from "antd";
import { ReloadOutlined, SearchOutlined, FilterOutlined } from "@ant-design/icons";

export default function Toolbar({ keyword, onKeywordChange, status, onStatusChange, statusOptions = [], onSearch, onReload, placeholder = "Tìm kiếm...", children }) {
  return (
    <Card className="toolbar-card" bordered={false}>
      <Space wrap className="toolbar-space">
        {onKeywordChange ? (
          <Input
            allowClear
            prefix={<SearchOutlined />}
            placeholder={placeholder}
            value={keyword}
            onChange={(event) => onKeywordChange?.(event.target.value)}
            onPressEnter={onSearch}
            style={{ width: 340 }}
          />
        ) : null}
        {statusOptions.length ? (
          <Select
            allowClear
            placeholder="Trạng thái"
            value={status || undefined}
            onChange={onStatusChange}
            options={statusOptions.map((item) => ({ value: item, label: item }))}
            style={{ width: 220 }}
          />
        ) : null}
        {children}
        <Button icon={<ReloadOutlined />} onClick={onReload}>Tải lại</Button>
        {onSearch ? (
          <Button type="primary" icon={<FilterOutlined />} onClick={onSearch}>Lọc</Button>
        ) : null}
      </Space>
    </Card>
  );
}
