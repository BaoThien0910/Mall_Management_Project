import { Button, Card, Input, Select, Space } from "antd";
import { ReloadOutlined, SearchOutlined } from "@ant-design/icons";

export default function Toolbar({ keyword, onKeywordChange, status, onStatusChange, statusOptions = [], onSearch, onReload, children }) {
  return (
    <Card className="toolbar-card" bordered={false}>
      <Space wrap className="toolbar-space">
        <Input
          allowClear
          prefix={<SearchOutlined />}
          placeholder="Tìm kiếm..."
          value={keyword}
          onChange={(event) => onKeywordChange?.(event.target.value)}
          onPressEnter={onSearch}
          style={{ width: 280 }}
        />
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
        <Button type="primary" icon={<SearchOutlined />} onClick={onSearch}>Lọc</Button>
      </Space>
    </Card>
  );
}
