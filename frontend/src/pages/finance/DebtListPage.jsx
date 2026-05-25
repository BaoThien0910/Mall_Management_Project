import { CalculatorOutlined } from "@ant-design/icons";
import { Alert, Card, Col, Form, InputNumber, Modal, Row, Typography, message } from "antd";
import { useCallback, useState } from "react";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { debtService } from "../../services/debtService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { formatMoney, pick, pickId } from "../../utils/data";

const { Text } = Typography;

export default function DebtListPage() {
  const [open, setOpen] = useState(false);
  const [calculateResult, setCalculateResult] = useState(null);
  const [form] = Form.useForm();

  const fetcher = useCallback((params) => debtService.list(params), []);
  const { items, loading, reload } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const calculate = async () => {
    try {
      const values = await form.validateFields();
      const result = await debtService.calculate(values);

      setCalculateResult(result);
      message.success("Đã tính công nợ");
      setOpen(false);
      form.resetFields();
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const columns = [
    {
      title: "Mã CN",
      render: (_, record) => pick(record, ["ma_cong_no", "ma_cn", "MACN"]),
    },
    {
      title: "Hợp đồng",
      render: (_, record) => pick(record, ["ma_hop_dong", "ma_hd", "MAHD"]),
    },
    {
      title: "Kỳ",
      render: (_, record) => `${pick(record, ["thang", "THANG"])} / ${pick(record, ["nam", "NAM"])}`,
    },
    {
      title: "Tiền thuê",
      render: (_, record) => formatMoney(pick(record, ["tien_thue", "TIENTHUE"])),
    },
    {
      title: "Tiền điện",
      render: (_, record) => formatMoney(pick(record, ["tien_dien", "TIENDIEN"])),
    },
    {
      title: "Tiền nước",
      render: (_, record) => formatMoney(pick(record, ["tien_nuoc", "TIENNUOC"])),
    },
    {
      title: "Phí bảo trì",
      render: (_, record) => formatMoney(pick(record, ["phi_bao_tri", "PHIBAOTRI"])),
    },
    {
      title: "Hoàn trả",
      render: (_, record) => formatMoney(pick(record, ["tien_hoan", "TIENHOAN"])),
    },
    {
      title: "Tổng tiền",
      render: (_, record) => formatMoney(pick(record, ["tong_tien", "TONGTIEN"])),
    },
    {
      title: "Hạn thanh toán",
      render: (_, record) => pick(record, ["han_thanh_toan", "HAN_THANHTOAN"], "-"),
    },
    {
      title: "Trạng thái",
      render: (_, record) => <StatusTag value={pick(record, ["trang_thai", "TRANGTHAI"])} />,
    },
  ];

  return (
    <>
      <PageHeader
        title="Công nợ"
        breadcrumb={["Tài chính", "Công nợ"]}
        actionText="Tính công nợ"
        actionIcon={<CalculatorOutlined />}
        onAction={() => setOpen(true)}
      />

      {calculateResult ? (
        <Card className="section-card">
          <Row gutter={[16, 16]}>
            <Col xs={12} md={6}>
              <Text type="secondary">Đã tạo</Text>
              <h2 className="stat-value">{calculateResult.so_cong_no_da_tao || 0}</h2>
            </Col>
            <Col xs={12} md={6}>
              <Text type="secondary">Bỏ qua</Text>
              <h2 className="stat-value">{calculateResult.so_cong_no_bo_qua || 0}</h2>
            </Col>
            <Col xs={12} md={6}>
              <Text type="secondary">Thiếu chỉ số</Text>
              <h2 className="stat-value stat-danger">{calculateResult.so_hop_dong_thieu_chi_so || 0}</h2>
            </Col>
            <Col xs={12} md={6}>
              <Text type="secondary">Thiếu import</Text>
              <h2 className="stat-value stat-danger">{calculateResult.so_hop_dong_thieu_du_lieu || 0}</h2>
            </Col>
          </Row>

          {calculateResult.danh_sach_thieu_chi_so?.length ? (
            <Alert
              className="mt-16"
              type="warning"
              showIcon
              message="Có hợp đồng thiếu chỉ số điện nước"
              description={calculateResult.danh_sach_thieu_chi_so
                .map((item) => `${item.ma_hop_dong} - ${item.ma_mat_bang}: ${item.ly_do}`)
                .join("; ")}
            />
          ) : null}

          {calculateResult.danh_sach_thieu_du_lieu?.length ? (
            <Alert
              className="mt-16"
              type="error"
              showIcon
              message="Có hợp đồng thiếu dữ liệu import"
              description={calculateResult.danh_sach_thieu_du_lieu
                .map((item) => `${item.ma_hop_dong}: ${item.ly_do}`)
                .join("; ")}
            />
          ) : null}
        </Card>
      ) : null}

      <ResponsiveTable
        rowKey={(record) => pickId(record, ["ma_cong_no", "ma_cn", "MACN"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title="Tính công nợ tháng"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={calculate}
        okText="Tính công nợ"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical">
          <Form.Item label="Tháng" name="thang" rules={[{ required: true, message: "Nhập tháng" }]}>
            <InputNumber min={1} max={12} style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item label="Năm" name="nam" rules={[{ required: true, message: "Nhập năm" }]}>
            <InputNumber min={2000} max={2100} style={{ width: "100%" }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
