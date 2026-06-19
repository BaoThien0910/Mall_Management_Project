import { Table } from "antd";

export default function ResponsiveTable({ rowKey = "id", columns, dataSource, loading, ...rest }) {
  return (
    <Table
      rowKey={rowKey}
      columns={columns}
      dataSource={dataSource}
      loading={loading}
      pagination={{ pageSize: 8, showSizeChanger: false }}
      scroll={{ x: 980 }}
      className="app-table-card"
      {...rest}
    />
  );
}
