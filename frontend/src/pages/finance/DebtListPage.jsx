import { CalculatorOutlined, FilterOutlined } from "@ant-design/icons";
import { Alert, Card, Col, Form, InputNumber, Modal, Row, Typography, message, Popover, Select, Space, Button } from "antd";
import { useCallback, useState, useRef, useEffect } from "react";
import Toolbar from "../../components/common/Toolbar";
import { CONG_NO_STATUS } from "../../constants/statuses";

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

  const [keyword, setKeyword] = useState("");
  const [popoverOpen, setPopoverOpen] = useState(false);
  const timerRef = useRef(null);

  const [appliedFilters, setAppliedFilters] = useState({
    nam: undefined,
    trang_thai: undefined,
  });

  const [tempNam, setTempNam] = useState(undefined);
  const [tempTrangThai, setTempTrangThai] = useState(undefined);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  const fetcher = useCallback((params) => debtService.list(params), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const applySearch = (val) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    timerRef.current = setTimeout(() => {
      const activeFilters = {};
      Object.keys(appliedFilters).forEach((key) => {
        if (appliedFilters[key] !== undefined && appliedFilters[key] !== null && appliedFilters[key] !== "") {
          activeFilters[key] = appliedFilters[key];
        }
      });
      setParams({
        keyword: val || undefined,
        ...activeFilters,
        page: 1,
        page_size: 20,
      });
    }, 500);
  };

  const handleApply = () => {
    const nextFilters = {
      nam: tempNam || undefined,
      trang_thai: tempTrangThai || undefined,
    };
    setAppliedFilters(nextFilters);

    const cleanFilters = {};
    Object.keys(nextFilters).forEach((key) => {
      if (nextFilters[key] !== undefined && nextFilters[key] !== null && nextFilters[key] !== "") {
        cleanFilters[key] = nextFilters[key];
      }
    });

    setParams({
      keyword: keyword || undefined,
      ...cleanFilters,
      page: 1,
      page_size: 20,
    });
    setPopoverOpen(false);
  };

  const handleCancel = () => {
    setTempNam(appliedFilters.nam);
    setTempTrangThai(appliedFilters.trang_thai);
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempNam(undefined);
    setTempTrangThai(undefined);

    setAppliedFilters({
      nam: undefined,
      trang_thai: undefined,
    });
    setPopoverOpen(false);

    setParams({
      keyword: keyword || undefined,
      page: 1,
      page_size: 20,
    });
  };

  const handleReload = () => {
    setKeyword("");
    setAppliedFilters({
      nam: undefined,
      trang_thai: undefined,
    });
    setTempNam(undefined);
    setTempTrangThai(undefined);
    setParams({
      page: 1,
      page_size: 20,
    });
    reload();
  };

  const activeFiltersCount =
    (appliedFilters.nam ? 1 : 0) +
    (appliedFilters.trang_thai ? 1 : 0);

  const filterContent = (
    <div style={{ padding: "8px", width: 300 }}>
      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Năm</div>
        <InputNumber
          placeholder="Nhập năm (VD: 2026)"
          value={tempNam}
          onChange={setTempNam}
          style={{ width: "100%" }}
          min={2000}
          max={2100}
          precision={0}
        />
      </div>

      <div style={{ marginBottom: "20px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Trạng thái</div>
        <Select
          placeholder="Chọn trạng thái"
          value={tempTrangThai}
          onChange={setTempTrangThai}
          style={{ width: "100%" }}
          allowClear
          options={CONG_NO_STATUS.map((item) => ({ value: item, label: item }))}
        />
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Button type="primary" danger onClick={handleClearFilters}>
          Xóa bộ lọc
        </Button>
        <Space>
          <Button onClick={handleCancel}>Hủy</Button>
          <Button type="primary" onClick={handleApply}>
            Áp dụng
          </Button>
        </Space>
      </div>
    </div>
  );

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

      <Toolbar
        keyword={keyword}
        onKeywordChange={(val) => {
          setKeyword(val);
          applySearch(val);
        }}
        placeholder="Tìm kiếm mã Hợp đồng"
        onReload={handleReload}
      >
        <Popover
          content={filterContent}
          trigger="click"
          open={popoverOpen}
          onOpenChange={(visible) => {
            setPopoverOpen(visible);
            if (!visible) {
              handleCancel();
            }
          }}
          placement="bottomLeft"
          overlayStyle={{ zIndex: 1050 }}
        >
          <Button
            type="primary"
            icon={<FilterOutlined />}
            style={{
              minWidth: 100,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span style={{ display: "inline-flex", alignItems: "center" }}>Lọc</span>
            {activeFiltersCount > 0 && (
              <span
                style={{
                  marginLeft: 8,
                  backgroundColor: "#fff",
                  color: "#1677ff",
                  borderRadius: "50%",
                  width: "20px",
                  height: "20px",
                  fontSize: "12px",
                  fontWeight: 600,
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  lineHeight: "1",
                }}
              >
                {activeFiltersCount}
              </span>
            )}
          </Button>
        </Popover>
      </Toolbar>

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
