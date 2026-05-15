import React, { useMemo, useState } from 'react';
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
} from 'antd';
import {
  SearchOutlined,
  EyeOutlined,
  CreditCardOutlined,
  CalculatorOutlined,
  UploadOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { MOCK_DEBTS } from '../../services/debtService';
import { DEBT_STATUS } from '../../constants/financeConstants';
import { formatCurrency, formatDate } from '../../utils/format';

const { Title, Text } = Typography;
const { Option } = Select;

const TENANT_NAME = 'Starbucks';

export default function DebtListPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const isTenant = location.pathname.startsWith('/tenant');
  const basePath = isTenant ? '/tenant/billing' : '/staff/finance';

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState(null);

  const debts = useMemo(() => {
    let list = MOCK_DEBTS;
    if (isTenant) {
      list = list.filter((d) => d.tenant === TENANT_NAME);
    }
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(
        (d) =>
          d.id.toLowerCase().includes(q) ||
          d.tenant.toLowerCase().includes(q) ||
          d.premise.toLowerCase().includes(q)
      );
    }
    if (statusFilter) {
      list = list.filter((d) => d.status === statusFilter);
    }
    return list;
  }, [isTenant, search, statusFilter]);

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
      render: (status) => {
        const cfg = DEBT_STATUS[status] || { label: status, color: 'default' };
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
            <Statistic title="Số kỳ công nợ" value={summary.count} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card style={{ borderRadius: 8 }}>
            <Statistic
              title="Tổng còn phải trả"
              value={summary.remaining}
              formatter={(v) => formatCurrency(v)}
              valueStyle={{ color: '#cf1322', fontSize: 18 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card style={{ borderRadius: 8 }}>
            <Statistic title="Kỳ quá hạn" value={summary.overdue} valueStyle={{ color: '#fa8c16' }} />
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

      <Table
        columns={columns}
        dataSource={debts.map((d) => ({ ...d, key: d.id }))}
        style={{ backgroundColor: '#fff', borderRadius: 8 }}
        pagination={{ pageSize: 10 }}
        scroll={{ x: isTenant ? 900 : 1100 }}
      />
    </>
  );
}

