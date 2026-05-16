import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Table,
  Typography,
  Card,
  Space,
  Input,
  DatePicker,
  Button,
  Tag,
  Skeleton,
  Empty,
  message,
} from 'antd';
import { SearchOutlined, ArrowLeftOutlined, DownloadOutlined } from '@ant-design/icons';
import { fetchInvoices } from '../../services/paymentService';
import { PAYMENT_METHODS } from '../../constants/financeConstants';
import { formatCurrency, formatDate } from '../../utils/format';

const { Title } = Typography;
const { RangePicker } = DatePicker;

export default function InvoiceHistoryPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const isTenant = location.pathname.startsWith('/tenant');
  const basePath = isTenant ? '/tenant/billing' : '/staff/finance';

  const [search, setSearch] = useState('');
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const list = await fetchInvoices({ limit: 500, skip: 0 });
        if (!cancelled) setRows(list);
      } catch {
        if (!cancelled) message.error('Không tải được lịch sử hóa đơn');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const invoices = useMemo(() => {
    if (!search) return rows;
    const q = search.toLowerCase();
    return rows.filter(
      (i) =>
        (i.invoiceNo || '').toLowerCase().includes(q) ||
        (i.debtId || '').toLowerCase().includes(q) ||
        (i.tenant || '').toLowerCase().includes(q)
    );
  }, [rows, search]);

  const methodMap = Object.fromEntries(PAYMENT_METHODS.map((m) => [m.value, m.label]));

  const columns = [
    { title: 'Số hóa đơn', dataIndex: 'invoiceNo', key: 'invoiceNo', width: 150 },
    { title: 'Mã công nợ', dataIndex: 'debtId', key: 'debtId', width: 140 },
    ...(!isTenant ? [{ title: 'Khách thuê', dataIndex: 'tenant', key: 'tenant' }] : []),
    { title: 'Kỳ', dataIndex: 'period', key: 'period', width: 90 },
    {
      title: 'Số tiền',
      dataIndex: 'amount',
      key: 'amount',
      align: 'right',
      render: (v) => formatCurrency(v),
    },
    {
      title: 'Ngày thanh toán',
      dataIndex: 'paidAt',
      key: 'paidAt',
      width: 130,
      render: (d) => formatDate(d),
    },
    {
      title: 'Phương thức',
      dataIndex: 'method',
      key: 'method',
      render: (m) => <Tag>{methodMap[m] || m}</Tag>,
    },
    {
      title: 'Thao tác',
      key: 'action',
      width: 100,
      render: () => (
        <Button type="link" size="small" icon={<DownloadOutlined />}>
          Tải PDF
        </Button>
      ),
    },
  ];

  return (
    <>
      <Button icon={<ArrowLeftOutlined />} style={{ marginBottom: 16 }} onClick={() => navigate(basePath)}>
        Quay lại
      </Button>

      <Title level={3} style={{ marginBottom: 24 }}>
        Lịch sử hóa đơn
      </Title>

      <Card bodyStyle={{ padding: 16 }} style={{ marginBottom: 24, borderRadius: 8 }}>
        <Space wrap size="middle">
          <Input
            placeholder="Tìm số HĐ, mã CN, khách thuê..."
            prefix={<SearchOutlined />}
            style={{ width: 300 }}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
          />
          <RangePicker style={{ width: 280 }} />
        </Space>
      </Card>

      {loading && rows.length === 0 ? (
        <Skeleton active paragraph={{ rows: 8 }} />
      ) : invoices.length === 0 ? (
        <Card>
          <Empty description="Chưa có hóa đơn" />
        </Card>
      ) : (
        <Table
          columns={columns}
          dataSource={invoices}
          loading={loading}
          style={{ backgroundColor: '#fff', borderRadius: 8 }}
          pagination={{ pageSize: 10 }}
          locale={{ emptyText: 'Không có dữ liệu' }}
          scroll={{ x: 900 }}
        />
      )}
    </>
  );
}
