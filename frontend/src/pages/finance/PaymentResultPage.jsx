import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Result, Button, Card, Descriptions, Typography } from 'antd';
import { formatCurrency, formatDate } from '../../utils/format';
import { PAYMENT_METHODS } from '../../constants/financeConstants';

const { Text } = Typography;

export default function PaymentResultPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state || {};
  const basePath = '/tenant/billing';

  const methodLabel =
    PAYMENT_METHODS.find((m) => m.value === state.method)?.label || state.method || '—';

  if (state.success) {
    return (
      <Card style={{ maxWidth: 640, margin: '0 auto', borderRadius: 8 }}>
        <Result
          status="success"
          title="Thanh toán thành công"
          subTitle="Giao dịch của bạn đã được ghi nhận. Hóa đơn điện tử sẽ được gửi qua email."
          extra={[
            <Button type="primary" key="list" onClick={() => navigate(basePath)}>
              Về danh sách công nợ
            </Button>,
            <Button key="invoices" onClick={() => navigate(`${basePath}/invoices`)}>
              Xem hóa đơn
            </Button>,
          ]}
        />
        <Descriptions bordered column={1} size="small" style={{ marginTop: 24 }}>
          <Descriptions.Item label="Mã giao dịch">{state.transactionId}</Descriptions.Item>
          <Descriptions.Item label="Mã công nợ">{state.debtId}</Descriptions.Item>
          <Descriptions.Item label="Số tiền">{formatCurrency(state.amount)}</Descriptions.Item>
          <Descriptions.Item label="Phương thức">{methodLabel}</Descriptions.Item>
          <Descriptions.Item label="Thời gian">
            {state.paidAt ? formatDate(state.paidAt) : '—'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    );
  }

  return (
    <Card style={{ maxWidth: 640, margin: '0 auto', borderRadius: 8 }}>
      <Result
        status="error"
        title="Thanh toán thất bại"
        subTitle="Giao dịch không hoàn tất. Vui lòng thử lại hoặc liên hệ ban quản lý."
        extra={[
          <Button
            type="primary"
            key="retry"
            onClick={() => navigate(state.debtId ? `${basePath}/pay/${state.debtId}` : basePath)}
          >
            Thử lại
          </Button>,
          <Button key="back" onClick={() => navigate(basePath)}>
            Về danh sách
          </Button>,
        ]}
      />
      {state.debtId && (
        <Text type="secondary" style={{ display: 'block', textAlign: 'center' }}>
          Mã công nợ: {state.debtId}
        </Text>
      )}
    </Card>
  );
}
