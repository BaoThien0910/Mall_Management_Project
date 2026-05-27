import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Upload,
  Button,
  Space,
  Table,
  Alert,
  Steps,
  message,
  Row,
  Col,
} from 'antd';
import {
  ArrowLeftOutlined,
  InboxOutlined,
  DownloadOutlined,
  CalculatorOutlined,
} from '@ant-design/icons';
import { importFinancialFile } from '../../services/paymentService';
import { calculateDebt } from '../../services/debtService';

const { Title, Text } = Typography;
const { Dragger } = Upload;

const MOCK_PREVIEW = [
  { key: '1', tenant: 'Starbucks', premise: 'GF-01', period: '11/2025', rent: 38000000, utility: 5100000, status: 'Hợp lệ' },
  { key: '2', tenant: 'Uniqlo', premise: 'L2-12', period: '11/2025', rent: 75000000, utility: 6800000, status: 'Hợp lệ' },
  { key: '3', tenant: 'Highlands Coffee', premise: 'GF-08', period: '11/2025', rent: 24000000, utility: 3200000, status: 'Thiếu chỉ số điện' },
];

export default function FinancialImportPage() {
  const navigate = useNavigate();
  const basePath = '/staff/finance';
  const [fileList, setFileList] = useState([]);
  const [step, setStep] = useState(0);
  const [importing, setImporting] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [preview] = useState(MOCK_PREVIEW);

  const handleImport = async () => {
    if (fileList.length === 0) {
      message.warning('Vui lòng chọn file Excel trước khi nhập dữ liệu');
      return;
    }
    setImporting(true);
    try {
      const formData = new FormData();
      formData.append('file', fileList[0].originFileObj || fileList[0]);
      const result = await importFinancialFile(formData);
      message.success(result.message || `Đã nhập ${result.imported} dòng dữ liệu`);
      setStep(1);
    } catch {
      message.error('Nhập dữ liệu thất bại');
    } finally {
      setImporting(false);
    }
  };

  const handleCalculate = async () => {
    setCalculating(true);
    try {
      await calculateDebt({ period: '11/2025' });
      message.success('Đã tính toán công nợ cho kỳ 11/2025');
      setStep(2);
    } catch {
      message.error('Tính công nợ thất bại');
    } finally {
      setCalculating(false);
    }
  };

  const columns = [
    { title: 'Khách thuê', dataIndex: 'tenant', key: 'tenant' },
    { title: 'Mặt bằng', dataIndex: 'premise', key: 'premise', width: 100 },
    { title: 'Kỳ', dataIndex: 'period', key: 'period', width: 90 },
    {
      title: 'Tiền thuê',
      dataIndex: 'rent',
      key: 'rent',
      align: 'right',
      render: (v) => v?.toLocaleString('vi-VN'),
    },
    {
      title: 'Điện nước',
      dataIndex: 'utility',
      key: 'utility',
      align: 'right',
      render: (v) => v?.toLocaleString('vi-VN'),
    },
    {
      title: 'Kiểm tra',
      dataIndex: 'status',
      key: 'status',
      render: (s) => (
        <Text type={s === 'Hợp lệ' ? 'success' : 'danger'}>{s}</Text>
      ),
    },
  ];

  return (
    <>
      <Button
        icon={<ArrowLeftOutlined />}
        style={{ marginBottom: 16 }}
        onClick={() => navigate(basePath)}
      >
        Quay lại công nợ
      </Button>

      <Title level={3} style={{ marginBottom: 24 }}>
        Nhập dữ liệu & Tính công nợ
      </Title>

      <Steps
        current={step}
        style={{ marginBottom: 32, maxWidth: 720 }}
        items={[
          { title: 'Tải file Excel' },
          { title: 'Kiểm tra dữ liệu' },
          { title: 'Tính công nợ' },
        ]}
      />

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={10}>
          <Card title="1. Tải file lên" style={{ borderRadius: 8, marginBottom: 24 }}>
            <Alert
              type="info"
              message="Chấp nhận file .xlsx, .xls. Dữ liệu sẽ được xử lý khi kết nối máy chủ."
              style={{ marginBottom: 16 }}
            />
            <Dragger
              accept=".xlsx,.xls"
              maxCount={1}
              fileList={fileList}
              beforeUpload={() => false}
              onChange={({ fileList: fl }) => setFileList(fl)}
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">Kéo thả hoặc bấm để chọn file Excel</p>
              <p className="ant-upload-hint">Dữ liệu tiền thuê, điện nước, phí dịch vụ theo kỳ</p>
            </Dragger>
            <Space style={{ marginTop: 16 }} wrap>
              <Button icon={<DownloadOutlined />}>Tải mẫu Excel</Button>
              <Button type="primary" loading={importing} onClick={handleImport}>
                Nhập dữ liệu
              </Button>
            </Space>
          </Card>

          <Card title="2. Tính công nợ" style={{ borderRadius: 8 }}>
            <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
              Sau khi nhập và kiểm tra, hệ thống sẽ tạo công nợ theo hợp đồng và chỉ số điện nước.
            </Text>
            <Button
              type="primary"
              icon={<CalculatorOutlined />}
              loading={calculating}
              disabled={step < 1}
              onClick={handleCalculate}
            >
              Tính công nợ kỳ hiện tại
            </Button>
          </Card>
        </Col>

        <Col xs={24} lg={14}>
          <Card title="Xem trước dữ liệu" style={{ borderRadius: 8 }}>
            <Table
              columns={columns}
              dataSource={preview}
              pagination={false}
              size="small"
              scroll={{ x: 600 }}
            />
          </Card>
        </Col>
      </Row>
    </>
  );
}
