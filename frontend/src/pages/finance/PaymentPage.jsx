import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Typography,
  Card,
  Form,
  InputNumber,
  Select,
  Button,
  Space,
  Descriptions,
  Spin,
  message,
  Alert,
  Row,
  Col,
} from 'antd';
import { ArrowLeftOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import { fetchDebtById } from '../../services/debtService';
import { createPayment } from '../../services/paymentService';
import { PAYMENT_METHODS } from '../../constants/financeConstants';
import { formatCurrency, formatDate } from '../../utils/format';

const { Title, Text } = Typography;
const { Option } = Select;

export default function PaymentPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [debt, setDebt] = useState(null);

  const basePath = '/tenant/billing';

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const data = await fetchDebtById(id);
        if (!cancelled) {
          setDebt(data);
          const remaining = (data.totalAmount || 0) - (data.paidAmount || 0);
          form.setFieldsValue({ amount: remaining, method: 'vnpay' });
        }
      } catch {
        if (!cancelled) message.error('Không tải được thông tin thanh toán');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id, form]);

  const onFinish = async (values) => {
    setSubmitting(true);
    try {
      const result = await createPayment({
        debtId: id,
        amount: values.amount,
        method: values.method,
      });
      navigate(`${basePath}/pay/result`, {
        state: {
          success: true,
          debtId: id,
          amount: values.amount,
          method: values.method,
          transactionId: result.transactionId,
          paidAt: result.paidAt,
        },
      });
    } catch {
      navigate(`${basePath}/pay/result`, {
        state: { success: false, debtId: id },
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 48 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!debt) {
    return <Title level={4}>Không tìm thấy công nợ để thanh toán</Title>;
  }

  const remaining = (debt.totalAmount || 0) - (debt.paidAmount || 0);

  return (
    <>
      <Button
        icon={<ArrowLeftOutlined />}
        style={{ marginBottom: 24 }}
        onClick={() => navigate(`${basePath}/${id}`)}
      >
        Quay lại chi tiết
      </Button>

      <Title level={3} style={{ marginBottom: 24 }}>
        Thanh toán công nợ
      </Title>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={14}>
          <Card title="Thông tin thanh toán" style={{ borderRadius: 8 }}>
            <Alert
              type="info"
              showIcon
              icon={<SafetyCertificateOutlined />}
              message="Giao dịch được mã hóa an toàn. Vui lòng kiểm tra số tiền trước khi xác nhận."
              style={{ marginBottom: 24 }}
            />
            <Form form={form} layout="vertical" onFinish={onFinish}>
              <Form.Item
                name="amount"
                label="Số tiền thanh toán (VND)"
                rules={[
                  { required: true, message: 'Vui lòng nhập số tiền' },
                  {
                    type: 'number',
                    max: remaining,
                    message: `Số tiền không vượt quá ${formatCurrency(remaining)}`,
                  },
                  {
                    type: 'number',
                    min: 1000,
                    message: 'Số tiền tối thiểu 1.000 VND',
                  },
                ]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={(v) => v.replace(/,/g, '')}
                  min={0}
                  max={remaining}
                />
              </Form.Item>

              <Form.Item
                name="method"
                label="Phương thức thanh toán"
                rules={[{ required: true, message: 'Vui lòng chọn phương thức' }]}
              >
                <Select placeholder="Chọn phương thức">
                  {PAYMENT_METHODS.map((m) => (
                    <Option key={m.value} value={m.value}>
                      {m.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item style={{ marginBottom: 0 }}>
                <Space wrap>
                  <Button onClick={() => navigate(basePath)}>Hủy</Button>
                  <Button type="primary" htmlType="submit" loading={submitting}>
                    Xác nhận thanh toán
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card title="Tóm tắt công nợ" style={{ borderRadius: 8 }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Mã">{debt.id}</Descriptions.Item>
              <Descriptions.Item label="Kỳ">{debt.period}</Descriptions.Item>
              <Descriptions.Item label="Hạn">{formatDate(debt.dueDate)}</Descriptions.Item>
              <Descriptions.Item label="Tổng phải trả">
                {formatCurrency(debt.totalAmount)}
              </Descriptions.Item>
              <Descriptions.Item label="Đã trả">{formatCurrency(debt.paidAmount)}</Descriptions.Item>
              <Descriptions.Item label="Còn lại">
                <Text type="danger" strong>
                  {formatCurrency(remaining)}
                </Text>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>
    </>
  );
}

