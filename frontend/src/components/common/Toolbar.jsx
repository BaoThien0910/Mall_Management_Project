import { Button, Card, Input, Select, Space } from "antd";
import { ReloadOutlined, SearchOutlined, FilterOutlined } from "@ant-design/icons";

export default function Toolbar({
  keyword,
  onKeywordChange,
  status,
  onStatusChange,
  statusOptions = [],
  onSearch,
  onReload,
  placeholder = "Tìm kiếm...",
  reloadAfterChildren = false,
  children,
}) {
  return (
    <Card className="toolbar-card" bordered={false} style={{ marginBottom: "16px" }} styles={{ body: { padding: "16px" } }}>
      <Space wrap className="toolbar-space" size={12}>
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
        {!reloadAfterChildren && onReload ? (
          <Button icon={<ReloadOutlined />} onClick={onReload} style={{ minWidth: 100 }}>
            Tải lại
          </Button>
        ) : null}
        {children}
        {reloadAfterChildren && onReload ? (
          <Button icon={<ReloadOutlined />} onClick={onReload} style={{ minWidth: 100 }}>
            Tải lại
          </Button>
        ) : null}
        {onSearch ? (
          <Button type="primary" icon={<FilterOutlined />} onClick={onSearch} style={{ minWidth: 100 }}>
            Lọc
          </Button>
        ) : null}
      </Space>
    </Card>
  );
}
