import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Table,
  Typography,
  Tag,
  Space,
  Card,
  Input,
  Select,
  Button,
  Row,
  Col,
  Statistic,
  Skeleton,
  Empty,
} from 'antd';
import {
  SearchOutlined,
  EyeOutlined,
  CreditCardOutlined,
  CalculatorOutlined,
  UploadOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { fetchDebts } from '../../services/debtService';
import { DEBT_STATUS } from '../../constants/financeConstants';
import { formatCurrency, formatDate } from '../../utils/format';

const { Title, Text } = Typography;
const { Option } = Select;

export default function DebtListPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const isTenant = location.pathname.startsWith('/tenant');
  const basePath = isTenant ? '/tenant/billing' : '/staff/finance';

  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState(null);
  const [rawRows, setRawRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const h = window.setTimeout(() => setDebouncedSearch(search.trim()), 400);
    return () => window.clearTimeout(h);
  }, [search]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const params = {
          q: debouncedSearch || undefined,
          statusFil: statusFilter || undefined,
          limit: 500,
          skip: 0,
        };
        const rows = await fetchDebts(params);
        if (!cancelled) setRawRows(rows);
      } catch (e) {
        if (!cancelled) setError(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [debouncedSearch, statusFilter]);

  const debts = useMemo(() => rawRows, [rawRows]);

  const summary = useMemo(() => {
    const remaining = debts.reduce((sum, d) => sum + (d.totalAmount - d.paidAmount), 0);
    const overdue = debts.filter((d) => d.status === 'overdue').length;
    return { count: debts.length, remaining, overdue };
  }, [debts]);

  const columns = [
    { title: 'Mã công nợ', dataIndex: 'id', key: 'id', width: 140 },
    ...(!isTenant
      ? [
          { title: 'Khách thuê', dataIndex: 'tenant', key: 'tenant' },
          { title: 'Mặt bằng', dataIndex: 'premise', key: 'premise', width: 100 },
        ]
      : []),
    { title: 'Kỳ', dataIndex: 'period', key: 'period', width: 90 },
    {
      title: 'Hạn thanh toán',
      dataIndex: 'dueDate',
      key: 'dueDate',
      width: 130,
      render: (d) => formatDate(d),
    },
    {
      title: 'Tổng phải trả',
      dataIndex: 'totalAmount',
      key: 'totalAmount',
      align: 'right',
      render: (v) => formatCurrency(v),
    },
    {
      title: 'Đã trả',
      dataIndex: 'paidAmount',
      key: 'paidAmount',
      align: 'right',
      render: (v) => formatCurrency(v),
    },
    {
      title: 'Còn lại',
      key: 'remaining',
      align: 'right',
      render: (_, r) => (
        <Text strong type={r.status === 'overdue' ? 'danger' : undefined}>
          {formatCurrency(r.totalAmount - r.paidAmount)}
        </Text>
      ),
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      width: 150,
      render: (st) => {
        const cfg = DEBT_STATUS[st] || { label: st, color: 'default' };
        return <Tag color={cfg.color}>{cfg.label}</Tag>;
      },
    },
    {
      title: 'Thao tác',
      key: 'action',
      width: isTenant ? 180 : 120,
      fixed: 'right',
      render: (_, record) => {
        const canPay = record.status !== 'paid';
        return (
          <Space size="small" wrap>
            <Button
              type="link"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => navigate(`${basePath}/${record.id}`)}
            >
              Chi tiết
            </Button>
            {isTenant && canPay && (
              <Button
                type="primary"
                size="small"
                icon={<CreditCardOutlined />}
                onClick={() => navigate(`${basePath}/pay/${record.id}`)}
              >
                Thanh toán
              </Button>
            )}
          </Space>
        );
      },
    },
  ];

  const tableSkeleton = loading && debts.length === 0;

  return (
    <>
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: 16,
          marginBottom: 24,
        }}
      >
        <Title level={3} style={{ margin: 0 }}>
          {isTenant ? 'Công nợ & Thanh toán' : 'Quản lý Công nợ'}
        </Title>
        <Space wrap>
          {!isTenant && (
            <>
              <Button icon={<UploadOutlined />} onClick={() => navigate(`${basePath}/import`)}>
                Nhập dữ liệu
              </Button>
              <Button type="primary" icon={<CalculatorOutlined />} onClick={() => navigate(`${basePath}/import`)}>
                Tính công nợ
              </Button>
            </>
          )}
          <Button icon={<FileTextOutlined />} onClick={() => navigate(`${basePath}/invoices`)}>
            Lịch sử hóa đơn
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card style={{ borderRadius: 8 }}>
            {loading ? (
              <Skeleton active paragraph={{ rows: 1 }} />
            ) : (
              <Statistic title="Số kỳ công nợ" value={summary.count} />
            )}
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card style={{ borderRadius: 8 }}>
            {loading ? (
              <Skeleton active paragraph={{ rows: 1 }} />
            ) : (
              <Statistic
                title="Tổng còn phải trả"
                value={summary.remaining}
                formatter={(v) => formatCurrency(v)}
                valueStyle={{ color: '#cf1322', fontSize: 18 }}
              />
            )}
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card style={{ borderRadius: 8 }}>
            {loading ? (
              <Skeleton active paragraph={{ rows: 1 }} />
            ) : (
              <Statistic title="Kỳ quá hạn" value={summary.overdue} valueStyle={{ color: '#fa8c16' }} />
            )}
          </Card>
        </Col>
      </Row>

      <Card bodyStyle={{ padding: 16 }} style={{ marginBottom: 24, borderRadius: 8 }}>
        <Space wrap size="middle">
          <Input
            placeholder="Tìm mã CN, khách thuê, mặt bằng..."
            prefix={<SearchOutlined />}
            style={{ width: 280 }}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
          />
          <Select
            placeholder="Trạng thái"
            style={{ width: 180 }}
            allowClear
            value={statusFilter}
            onChange={setStatusFilter}
          >
            {Object.entries(DEBT_STATUS).map(([key, { label }]) => (
              <Option key={key} value={key}>
                {label}
              </Option>
            ))}
          </Select>
        </Space>
      </Card>

      {error ? (
        <Card>
          <Empty description={`Không tải được dữ liệu: ${error.message || ''}`} />
        </Card>
      ) : tableSkeleton ? (
        <Skeleton active paragraph={{ rows: 6 }} />
      ) : debts.length === 0 ? (
        <Card>
          <Empty description="Chưa có công nợ phù hợp" />
        </Card>
      ) : (
        <Table
          columns={columns}
          dataSource={debts.map((d) => ({ ...d, key: d.id }))}
          style={{ backgroundColor: '#fff', borderRadius: 8 }}
          pagination={{ pageSize: 10 }}
          loading={loading}
          locale={{ emptyText: 'Không có bản ghi' }}
          scroll={{ x: isTenant ? 900 : 1100 }}
        />
      )}
    </>
  );
}
