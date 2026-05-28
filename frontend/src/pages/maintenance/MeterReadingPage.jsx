import { ThunderboltOutlined } from "@ant-design/icons";
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Space,
  Typography,
  message,
} from "antd";
import { useCallback, useState } from "react";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import { meterService } from "../../services/meterService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { formatMoney, pick, pickId } from "../../utils/data";

const { Text } = Typography;

export default function MeterReadingPage() {
  const [open, setOpen] = useState(false);
  const [latestResult, setLatestResult] = useState(null);
  const [form] = Form.useForm();

  const fetcher = useCallback((params) => meterService.list(params), []);
  const { items, loading, reload } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const create = async () => {
    try {
      const values = await form.validateFields();
      const result = await meterService.create(values);

      message.success("Đã nhập chỉ số điện nước");
      setLatestResult(result);
      setOpen(false);
      form.resetFields();
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const columns = [
    {
      title: "Mã CSDN",
      render: (_, record) => pick(record, ["ma_chi_so_dien_nuoc", "ma_csdn", "MACSDN"]),
    },
    {
      title: "Mặt bằng",
      render: (_, record) => pick(record, ["ma_mat_bang", "ma_mb", "MAMB"]),
    },
    {
      title: "Tháng",
      render: (_, record) => `${pick(record, ["thang", "THANG"])} / ${pick(record, ["nam", "NAM"])}`,
    },
    {
      title: "Điện đầu",
      render: (_, record) => pick(record, ["chi_so_dien_dau", "CHISODIENDAU"]),
    },
    {
      title: "Điện cuối",
      render: (_, record) => pick(record, ["chi_so_dien_cuoi", "CHISODIENCUOI"]),
    },
    {
      title: "Số điện",
      render: (_, record) => pick(record, ["so_dien_tieu_thu", "SODIEN_TIEUTHU"]),
    },
    {
      title: "Tiền điện",
      render: (_, record) => formatMoney(pick(record, ["tien_dien", "TIENDIEN"])),
    },
    {
      title: "Nước đầu",
      render: (_, record) => pick(record, ["chi_so_nuoc_dau", "CHISONUOCDAU"]),
    },
    {
      title: "Nước cuối",
      render: (_, record) => pick(record, ["chi_so_nuoc_cuoi", "CHISONUOCCUOI"]),
    },
    {
      title: "Số nước",
      render: (_, record) => pick(record, ["so_nuoc_tieu_thu", "SONUOC_TIEUTHU"]),
    },
    {
      title: "Tiền nước",
      render: (_, record) => formatMoney(pick(record, ["tien_nuoc", "TIENNUOC"])),
    },
  ];

  return (
    <>
      <PageHeader
        title="Chỉ số điện nước"
        subtitle="Nhập chỉ số điện nước theo mặt bằng. Backend tự tính tiền điện/nước theo đơn giá cố định."
        breadcrumb={["Vận hành - Bảo trì", "Chỉ số điện nước"]}
        actionText="Nhập chỉ số"
        actionIcon={<ThunderboltOutlined />}
        onAction={() => setOpen(true)}
      />

      {latestResult ? (
        <Card className="section-card">
          <Space wrap size={24}>
            <Text strong>Số điện: {pick(latestResult, ["so_dien_tieu_thu", "SODIEN_TIEUTHU"], 0)}</Text>
            <Text strong>Tiền điện: {formatMoney(pick(latestResult, ["tien_dien", "TIENDIEN"], 0))}</Text>
            <Text strong>Số nước: {pick(latestResult, ["so_nuoc_tieu_thu", "SONUOC_TIEUTHU"], 0)}</Text>
            <Text strong>Tiền nước: {formatMoney(pick(latestResult, ["tien_nuoc", "TIENNUOC"], 0))}</Text>
          </Space>
        </Card>
      ) : null}

      <ResponsiveTable
        rowKey={(record) => pickId(record, ["ma_chi_so_dien_nuoc", "ma_csdn", "MACSDN"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title="Nhập chỉ số điện nước"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={create}
        okText="Lưu"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical">
          <Form.Item label="Mã mặt bằng" name="ma_mat_bang" rules={[{ required: true, message: "Nhập mã mặt bằng" }]}>
            <Input placeholder="Ví dụ: MB_TEST_001" />
          </Form.Item>
          <Form.Item label="Tháng" name="thang" rules={[{ required: true, message: "Nhập tháng" }]}>
            <InputNumber min={1} max={12} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Năm" name="nam" rules={[{ required: true, message: "Nhập năm" }]}>
            <InputNumber min={2000} max={2100} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Chỉ số điện đầu" name="chi_so_dien_dau" rules={[{ required: true, message: "Nhập chỉ số điện đầu" }]}>
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Chỉ số điện cuối" name="chi_so_dien_cuoi" rules={[{ required: true, message: "Nhập chỉ số điện cuối" }]}>
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Chỉ số nước đầu" name="chi_so_nuoc_dau" rules={[{ required: true, message: "Nhập chỉ số nước đầu" }]}>
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Chỉ số nước cuối" name="chi_so_nuoc_cuoi" rules={[{ required: true, message: "Nhập chỉ số nước cuối" }]}>
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
