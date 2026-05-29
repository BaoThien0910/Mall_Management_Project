import { PlusOutlined, FilterOutlined } from "@ant-design/icons";
import { Button, Form, Input, InputNumber, Modal, Space, message, Popover, DatePicker, Select } from "antd";
import { useCallback, useState, useEffect, useRef } from "react";
import dayjs from "dayjs";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import Toolbar from "../../components/common/Toolbar";
import { HOP_DONG_STATUS } from "../../constants/statuses";
import { contractService } from "../../services/contractService";
import { showApiError } from "../../services/apiClient";
import { pick, pickId, formatMoney, formatDate } from "../../utils/data";
import { useCrudList } from "../../hooks/useCrudList";

export default function ContractListPage() {
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();
  
  // Search keyword state (instant seeking)
  const [keyword, setKeyword] = useState("");
  
  // Popover open state
  const [popoverOpen, setPopoverOpen] = useState(false);
  
  // Applied filters state
  const [appliedFilters, setAppliedFilters] = useState({
    trang_thai: undefined,
    ngay_bat_dau_tu: undefined,
    ngay_bat_dau_den: undefined,
    ngay_ket_thuc_tu: undefined,
    ngay_ket_thuc_den: undefined,
    gia_thue_tu: undefined,
    gia_thue_den: undefined,
  });

  // Temporary filter states for the popover
  const [tempNgayBatDauTu, setTempNgayBatDauTu] = useState("");
  const [tempNgayBatDauDen, setTempNgayBatDauDen] = useState("");
  const [tempNgayKetThucTu, setTempNgayKetThucTu] = useState("");
  const [tempNgayKetThucDen, setTempNgayKetThucDen] = useState("");
  const [tempGiaThueTu, setTempGiaThueTu] = useState(null);
  const [tempGiaThueDen, setTempGiaThueDen] = useState(null);
  const [tempTrangThai, setTempTrangThai] = useState(undefined);

  const fetcher = useCallback((p) => contractService.list(p), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const timerRef = useRef(null);

  // Clean up timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  const applySearch = (val) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    timerRef.current = setTimeout(() => {
      setParams({
        keyword: val || undefined,
        ...appliedFilters,
        page: 1,
        page_size: 20,
      });
    }, 500);
  };

  const handleApply = () => {
    const nextFilters = {
      trang_thai: tempTrangThai || undefined,
      ngay_bat_dau_tu: tempNgayBatDauTu || undefined,
      ngay_bat_dau_den: tempNgayBatDauDen || undefined,
      ngay_ket_thuc_tu: tempNgayKetThucTu || undefined,
      ngay_ket_thuc_den: tempNgayKetThucDen || undefined,
      gia_thue_tu: tempGiaThueTu !== null && tempGiaThueTu !== "" ? tempGiaThueTu : undefined,
      gia_thue_den: tempGiaThueDen !== null && tempGiaThueDen !== "" ? tempGiaThueDen : undefined,
    };
    setAppliedFilters(nextFilters);
    setParams({
      keyword: keyword || undefined,
      ...nextFilters,
      page: 1,
      page_size: 20,
    });
    setPopoverOpen(false);
  };

  const handleCancel = () => {
    // Revert temp states back to the applied ones
    setTempNgayBatDauTu(appliedFilters.ngay_bat_dau_tu || "");
    setTempNgayBatDauDen(appliedFilters.ngay_bat_dau_den || "");
    setTempNgayKetThucTu(appliedFilters.ngay_ket_thuc_tu || "");
    setTempNgayKetThucDen(appliedFilters.ngay_ket_thuc_den || "");
    setTempGiaThueTu(appliedFilters.gia_thue_tu || null);
    setTempGiaThueDen(appliedFilters.gia_thue_den || null);
    setTempTrangThai(appliedFilters.trang_thai || undefined);
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempNgayBatDauTu("");
    setTempNgayBatDauDen("");
    setTempNgayKetThucTu("");
    setTempNgayKetThucDen("");
    setTempGiaThueTu(null);
    setTempGiaThueDen(null);
    setTempTrangThai(undefined);
  };

  const handleReload = () => {
    setKeyword("");
    const cleared = {
      trang_thai: undefined,
      ngay_bat_dau_tu: undefined,
      ngay_bat_dau_den: undefined,
      ngay_ket_thuc_tu: undefined,
      ngay_ket_thuc_den: undefined,
      gia_thue_tu: undefined,
      gia_thue_den: undefined,
    };
    setAppliedFilters(cleared);
    setTempNgayBatDauTu("");
    setTempNgayBatDauDen("");
    setTempNgayKetThucTu("");
    setTempNgayKetThucDen("");
    setTempGiaThueTu(null);
    setTempGiaThueDen(null);
    setTempTrangThai(undefined);
    setParams({
      page: 1,
      page_size: 20,
    });
  };

  const create = async () => {
    try {
      await contractService.create(form.getFieldsValue(true));
      message.success("Số hóa hợp đồng thành công");
      setOpen(false);
      form.resetFields();
      reload();
    } catch (e) {
      showApiError(e);
    }
  };

  const activeFiltersCount =
    (appliedFilters.trang_thai ? 1 : 0) +
    (appliedFilters.ngay_bat_dau_tu ? 1 : 0) +
    (appliedFilters.ngay_bat_dau_den ? 1 : 0) +
    (appliedFilters.ngay_ket_thuc_tu ? 1 : 0) +
    (appliedFilters.ngay_ket_thuc_den ? 1 : 0) +
    (appliedFilters.gia_thue_tu !== undefined && appliedFilters.gia_thue_tu !== null && appliedFilters.gia_thue_tu !== "" ? 1 : 0) +
    (appliedFilters.gia_thue_den !== undefined && appliedFilters.gia_thue_den !== null && appliedFilters.gia_thue_den !== "" ? 1 : 0);

  const filterContent = (
    <div style={{ padding: "8px", width: 440 }}>
      {/* Thời gian bắt đầu */}
      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Thời gian bắt đầu</div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ color: "#555" }}>From:</span>
          <DatePicker
            value={tempNgayBatDauTu ? dayjs(tempNgayBatDauTu) : null}
            onChange={(date) => setTempNgayBatDauTu(date ? dayjs(date).format("YYYY-MM-DD") : "")}
            format="DD/MM/YYYY"
            placeholder="Từ ngày"
            style={{ width: "100%" }}
            allowClear={false}
          />
          <span style={{ color: "#bfbfbf" }}>-</span>
          <span style={{ color: "#555" }}>To:</span>
          <DatePicker
            value={tempNgayBatDauDen ? dayjs(tempNgayBatDauDen) : null}
            onChange={(date) => setTempNgayBatDauDen(date ? dayjs(date).format("YYYY-MM-DD") : "")}
            format="DD/MM/YYYY"
            placeholder="Đến ngày"
            style={{ width: "100%" }}
            allowClear={false}
          />
        </div>
      </div>

      {/* Thời gian kết thúc */}
      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Thời gian kết thúc</div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ color: "#555" }}>From:</span>
          <DatePicker
            value={tempNgayKetThucTu ? dayjs(tempNgayKetThucTu) : null}
            onChange={(date) => setTempNgayKetThucTu(date ? dayjs(date).format("YYYY-MM-DD") : "")}
            format="DD/MM/YYYY"
            placeholder="Từ ngày"
            style={{ width: "100%" }}
            allowClear={false}
          />
          <span style={{ color: "#bfbfbf" }}>-</span>
          <span style={{ color: "#555" }}>To:</span>
          <DatePicker
            value={tempNgayKetThucDen ? dayjs(tempNgayKetThucDen) : null}
            onChange={(date) => setTempNgayKetThucDen(date ? dayjs(date).format("YYYY-MM-DD") : "")}
            format="DD/MM/YYYY"
            placeholder="Đến ngày"
            style={{ width: "100%" }}
            allowClear={false}
          />
        </div>
      </div>

      {/* Giá thuê */}
      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Giá thuê (đ)</div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <InputNumber
            placeholder="Từ"
            value={tempGiaThueTu}
            onChange={setTempGiaThueTu}
            style={{ width: "100%" }}
            formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
            parser={(value) => value.replace(/\$\s?|(,*)/g, "")}
            min={0}
          />
          <span style={{ color: "#bfbfbf" }}>-</span>
          <InputNumber
            placeholder="Đến"
            value={tempGiaThueDen}
            onChange={setTempGiaThueDen}
            style={{ width: "100%" }}
            formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
            parser={(value) => value.replace(/\$\s?|(,*)/g, "")}
            min={0}
          />
        </div>
      </div>

      {/* Trạng thái */}
      <div style={{ marginBottom: "20px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Trạng thái</div>
        <Select
          placeholder="Chọn trạng thái"
          value={tempTrangThai || undefined}
          onChange={setTempTrangThai}
          style={{ width: "100%" }}
          allowClear
          options={HOP_DONG_STATUS.map((item) => ({ value: item, label: item }))}
        />
      </div>

      {/* Footer */}
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

  const columns = [
    {
      title: "Mã HĐ",
      render: (_, r) => pick(r, ["ma_hop_dong", "ma_hd", "MAHD"]),
    },
    {
      title: "Khách thuê",
      render: (_, r) => pick(r, ["ma_khach_thue", "ma_kh", "MAKH"]),
    },
    {
      title: "Mặt bằng",
      render: (_, r) => pick(r, ["ma_mat_bang", "ma_mb", "MAMB"]),
    },
    {
      title: "Bắt đầu",
      render: (_, r) => formatDate(pick(r, ["ngay_bat_dau", "NGAYBATDAU"])),
    },
    {
      title: "Kết thúc",
      render: (_, r) => formatDate(pick(r, ["ngay_ket_thuc", "NGAYKETTHUC"])),
    },
    {
      title: "Giá thuê",
      render: (_, r) => formatMoney(pick(r, ["gia_thue_thang", "GIATHUETHANG"])),
    },
    {
      title: "Trạng thái",
      render: (_, r) => <StatusTag value={pick(r, ["trang_thai", "TRANGTHAI"])} />,
    },
  ];

  return (
    <>
      <PageHeader
        title="Số hóa & Quản lý hợp đồng"
        breadcrumb={["Hợp đồng"]}
        actionText="Số hóa hợp đồng"
        actionIcon={<PlusOutlined />}
        onAction={() => setOpen(true)}
      />
      <Toolbar
        keyword={keyword}
        onKeywordChange={(val) => {
          setKeyword(val);
          applySearch(val);
        }}
        placeholder="Tìm kiếm Mã HĐ, Khách thuê, Mặt bằng"
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
              display: "inline-flex",
              alignItems: "center",
              height: "38px",
              borderRadius: "8px",
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
        rowKey={(r) => pickId(r, ["ma_hop_dong", "ma_hd", "MAHD"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        width={720}
        title="Số hóa hợp đồng"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={create}
        okText="Tạo hợp đồng"
      >
        <Form form={form} layout="vertical">
          <Space direction="vertical" style={{ width: "100%" }}>
            <Form.Item name="ma_hop_dong" label="Mã hợp đồng" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="ma_khach_thue" label="Mã khách thuê" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="ma_mat_bang" label="Mã mặt bằng" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="ma_yeu_cau" label="Mã yêu cầu thuê thêm nếu có">
              <Input />
            </Form.Item>
            <Form.Item name="ngay_bat_dau" label="Ngày bắt đầu" rules={[{ required: true }]}>
              <Input type="date" />
            </Form.Item>
            <Form.Item name="ngay_ket_thuc" label="Ngày kết thúc" rules={[{ required: true }]}>
              <Input type="date" />
            </Form.Item>
            <Form.Item name="gia_thue_thang" label="Giá thuê tháng" rules={[{ required: true }]}>
              <InputNumber style={{ width: "100%" }} min={1} />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </>
  );
}
