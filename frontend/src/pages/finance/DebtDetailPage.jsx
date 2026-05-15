import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import {
  Typography,
  Card,
  Descriptions,
  Table,
  Tag,
  Button,
  Space,
  Spin,
  message,
} from 'antd';
import { ArrowLeftOutlined, CreditCardOutlined, DownloadOutlined } from '@ant-design/icons';
import { fetchDebtById } from '../../services/debtService';
import { DEBT_STATUS, INVOICE_TYPES } from '../../constants/financeConstants';
import { formatCurrency, formatDate } from '../../utils/format';

const { Title, Text } = Typography;

export default function DebtDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const isTenant = location.pathname.startsWith('/tenant');
  const basePath = isTenant ? '/tenant/billing' : '/staff/finance';

  const [loading, setLoading] = useState(true);
  const [debt, setDebt] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const data = await fetchDebtById(id);
        if (!cancelled) setDebt(data);
      } catch {
        if (!cancelled) message.error('Không tải được chi tiết công nợ');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 48 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!debt) {
    return <Title level={4}>Không tìm thấy công nợ</Title>;
  }

  const statusCfg = DEBT_STATUS[debt.status] || { label: debt.status, color: 'default' };
  const remaining = (debt.totalAmount || 0) - (debt.paidAmount || 0);
  const canPay = isTenant && debt.status !== 'paid' && remaining > 0;

  const lineColumns = [
    {
      title: 'Loại',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (t) => INVOICE_TYPES[t] || t,
    },
    { title: 'Mô tả', dataIndex: 'description', key: 'description' },
    {
      title: 'Số tiền',
      dataIndex: 'amount',
      key: 'amount',
      align: 'right',
      render: (v) => formatCurrency(v),
    },
  ];

  return (
    <>
      <Space style={{ marginBottom: 24 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(basePath)}>
          Quay lại
        </Button>
      </Space>

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
          Chi tiết công nợ {debt.id}
        </Title>
        <Space wrap>
          <Button icon={<DownloadOutlined />}>Xuất PDF</Button>
          {canPay && (
            <Button
              type="primary"
              icon={<CreditCardOutlined />}
              onClick={() => navigate(`${basePath}/pay/${debt.id}`)}
            >
              Thanh toán ngay
            </Button>
          )}
        </Space>
      </div>

      <Card style={{ marginBottom: 24, borderRadius: 8 }}>
        <Descriptions bordered column={{ xs: 1, sm: 2, lg: 3 }} size="middle">
          <Descriptions.Item label="Khách thuê">{debt.tenant}</Descriptions.Item>
          <Descriptions.Item label="Mặt bằng">{debt.premise}</Descriptions.Item>
          <Descriptions.Item label="Kỳ">{debt.period}</Descriptions.Item>
          <Descriptions.Item label="Hạn thanh toán">{formatDate(debt.dueDate)}</Descriptions.Item>
          <Descriptions.Item label="Trạng thái">
            <Tag color={statusCfg.color}>{statusCfg.label}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Tổng phải trả">
            <Text strong>{formatCurrency(debt.totalAmount)}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="Đã thanh toán">{formatCurrency(debt.paidAmount)}</Descriptions.Item>
          <Descriptions.Item label="Còn lại">
            <Text type={remaining > 0 ? 'danger' : 'success'} strong>
              {formatCurrency(remaining)}
            </Text>
          </Descriptions.Item>
          {debt.note && (
            <Descriptions.Item label="Ghi chú" span={3}>
              {debt.note}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      <Title level={5} style={{ marginBottom: 16 }}>
        Chi tiết các khoản
      </Title>
      <Table
        columns={lineColumns}
        dataSource={debt.lines || []}
        pagination={false}
        style={{ backgroundColor: '#fff', borderRadius: 8 }}
        scroll={{ x: 600 }}
        summary={() => (
          <Table.Summary.Row>
            <Table.Summary.Cell index={0} colSpan={2} align="end">
              <Text strong>Tổng cộng</Text>
            </Table.Summary.Cell>
            <Table.Summary.Cell index={1} align="right">
              <Text strong>{formatCurrency(debt.totalAmount)}</Text>
            </Table.Summary.Cell>
          </Table.Summary.Row>
        )}
      />
    </>
  );
}
