import { PlusOutlined, FilterOutlined } from "@ant-design/icons";
import {
  Descriptions,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  DatePicker,
  Popover,
  Space,
  Button,
  message,
} from "antd";
import { useCallback, useEffect, useMemo, useState, useRef } from "react";
import dayjs from "dayjs";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import Toolbar from "../../components/common/Toolbar";
import { HOP_DONG_STATUS } from "../../constants/statuses";
import { contractService } from "../../services/contractService";
import { lookupService } from "../../services/lookupService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import {
  pick,
  pickId,
  formatMoney,
  formatDate,
  toArray,
} from "../../utils/data";

function getTenantId(record) {
  return pick(record, ["ma_khach_thue", "ma_kh", "MAKH"], undefined);
}

function getPremiseId(record) {
  return pick(record, ["ma_mat_bang", "ma_mb", "MAMB"], undefined);
}

function getRentRequestId(record) {
  return pick(record, ["ma_yeu_cau", "ma_yc", "MAYC"], undefined);
}

export default function ContractListPage() {
  const { role } = useAuth();
  const canCreate = role === ROLE.QTV || role === ROLE.TP_KDTC || role === ROLE.NV_KDTC;

  const [open, setOpen] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [form] = Form.useForm();

  const [tenants, setTenants] = useState([]);
  const [vacantPremises, setVacantPremises] = useState([]);
  const [rentRequests, setRentRequests] = useState([]);
  const [selectedTenant, setSelectedTenant] = useState(null);
  const [selectedPremise, setSelectedPremise] = useState(null);
  const [selectedRentRequest, setSelectedRentRequest] = useState(null);
  const [loadingRentRequests, setLoadingRentRequests] = useState(false);

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

  const fetcher = useCallback((params) => contractService.list(params), []);
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

  const loadContractLookups = useCallback(async () => {
    try {
      const [tenantData, premiseData] = await Promise.all([
        lookupService.contractTenants(),
        lookupService.vacantPremises(),
      ]);

      setTenants(toArray(tenantData));
      setVacantPremises(toArray(premiseData));
    } catch (error) {
      showApiError(error);
    }
  }, []);

  useEffect(() => {
    if (canCreate) {
      loadContractLookups();
    }
  }, [loadContractLookups, canCreate]);

  const tenantOptions = useMemo(
    () =>
      tenants
        .map((item) => {
          const value = getTenantId(item);
          return {
            value,
            label:
              item.label ||
              `${value} - ${pick(item, ["ten_khach", "TENKHACH"], "")}`,
          };
        })
        .filter((item) => item.value),
    [tenants],
  );

  const vacantPremiseOptions = useMemo(
    () =>
      vacantPremises
        .map((item) => {
          const value = getPremiseId(item);
          return {
            value,
            label:
              item.label ||
              `${value} - ${pick(item, ["vi_tri", "VITRI"], "")} - Tầng ${pick(
                item,
                ["tang", "TANG"],
                "",
              )}`,
          };
        })
        .filter((item) => item.value),
    [vacantPremises],
  );

  const rentRequestOptions = useMemo(
    () =>
      rentRequests
        .map((item) => {
          const value = getRentRequestId(item);
          return {
            value,
            label:
              item.label ||
              `${value} - ${pick(item, ["ma_mat_bang", "MAMB"], "")} - ${pick(
                item,
                ["vi_tri", "VITRI"],
                "",
              )}`,
          };
        })
        .filter((item) => item.value),
    [rentRequests],
  );

  const openCreateModal = () => {
    form.resetFields();
    setSelectedTenant(null);
    setSelectedRentRequest(null);
    setSelectedPremise(null);
    setRentRequests([]);
    setOpen(true);
    loadContractLookups();
  };

  const handleTenantChange = async (value) => {
    const tenant = tenants.find((item) => getTenantId(item) === value);

    setSelectedTenant(tenant || null);
    setSelectedRentRequest(null);
    setSelectedPremise(null);
    setRentRequests([]);

    form.setFieldsValue({
      ma_yeu_cau: undefined,
      ma_mat_bang: undefined,
    });

    if (!value) return;

    setLoadingRentRequests(true);

    try {
      const data = await lookupService.approvedRentRequestsForContract(value);
      setRentRequests(toArray(data));
    } catch (error) {
      showApiError(error);
    } finally {
      setLoadingRentRequests(false);
    }
  };

  const handleRentRequestChange = (value) => {
    const request = rentRequests.find((item) => getRentRequestId(item) === value);

    setSelectedRentRequest(request || null);

    if (request) {
      form.setFieldsValue({
        ma_mat_bang: getPremiseId(request),
      });
      setSelectedPremise(request);
    } else {
      form.setFieldsValue({
        ma_mat_bang: undefined,
      });
      setSelectedPremise(null);
    }
  };

  const handlePremiseChange = (value) => {
    const premise = vacantPremises.find((item) => getPremiseId(item) === value);
    setSelectedPremise(premise || null);
  };

  const create = async () => {
    try {
      const values = await form.validateFields();

      const payload = {
        ...values,
        ma_yeu_cau: values.ma_yeu_cau || null,
        ngay_bat_dau: values.ngay_bat_dau?.format
          ? values.ngay_bat_dau.format("YYYY-MM-DD")
          : values.ngay_bat_dau,
        ngay_ket_thuc: values.ngay_ket_thuc?.format
          ? values.ngay_ket_thuc.format("YYYY-MM-DD")
          : values.ngay_ket_thuc,
      };

      await contractService.create(payload);

      message.success("Số hóa hợp đồng thành công");
      setOpen(false);
      form.resetFields();
      setSelectedTenant(null);
      setSelectedRentRequest(null);
      setSelectedPremise(null);
      setRentRequests([]);
      reload();
      loadContractLookups();
    } catch (error) {
      showApiError(error);
    }
  };

  const applySearch = (val) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    timerRef.current = setTimeout(() => {
      const activeFilters = {};
      Object.keys(appliedFilters).forEach(key => {
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
      trang_thai: tempTrangThai || undefined,
      ngay_bat_dau_tu: tempNgayBatDauTu || undefined,
      ngay_bat_dau_den: tempNgayBatDauDen || undefined,
      ngay_ket_thuc_tu: tempNgayKetThucTu || undefined,
      ngay_ket_thuc_den: tempNgayKetThucDen || undefined,
      gia_thue_tu: tempGiaThueTu !== null && tempGiaThueTu !== "" ? tempGiaThueTu : undefined,
      gia_thue_den: tempGiaThueDen !== null && tempGiaThueDen !== "" ? tempGiaThueDen : undefined,
    };
    setAppliedFilters(nextFilters);

    const cleanFilters = {};
    Object.keys(nextFilters).forEach(key => {
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

    setAppliedFilters({
      trang_thai: undefined,
      ngay_bat_dau_tu: undefined,
      ngay_bat_dau_den: undefined,
      ngay_ket_thuc_tu: undefined,
      ngay_ket_thuc_den: undefined,
      gia_thue_tu: undefined,
      gia_thue_den: undefined,
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
    reload();
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
      render: (_, record) => pick(record, ["ma_hop_dong", "ma_hd", "MAHD"]),
    },
    {
      title: "Khách thuê",
      render: (_, record) => pick(record, ["ma_khach_thue", "ma_kh", "MAKH"]),
    },
    {
      title: "Mặt bằng",
      render: (_, record) => pick(record, ["ma_mat_bang", "ma_mb", "MAMB"]),
    },
    {
      title: "Bắt đầu",
      render: (_, record) => formatDate(pick(record, ["ngay_bat_dau", "NGAYBATDAU"])),
    },
    {
      title: "Kết thúc",
      render: (_, record) => formatDate(pick(record, ["ngay_ket_thuc", "NGAYKETTHUC"])),
    },
    {
      title: "Giá thuê",
      render: (_, record) => formatMoney(pick(record, ["gia_thue_thang", "GIATHUETHANG"])),
    },
    {
      title: "Trạng thái",
      render: (_, record) => <StatusTag value={pick(record, ["trang_thai", "TRANGTHAI"])} />,
    },
  ];

  return (
    <>
      <PageHeader
        title="Hợp đồng"
        subtitle="Số hóa và theo dõi hợp đồng thuê mặt bằng"
        actionText="Số hóa hợp đồng"
        actionIcon={<PlusOutlined />}
        onAction={openCreateModal}
        actionDisabled={!canCreate}
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
        rowKey={(record) => pickId(record, ["ma_hop_dong", "ma_hd", "MAHD"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title="Số hóa hợp đồng"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={create}
        destroyOnClose
        okText="Tạo hợp đồng"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="ma_hop_dong"
            label="Mã hợp đồng"
            rules={[{ required: true, message: "Vui lòng nhập mã hợp đồng" }]}
          >
            <Input placeholder="Nhập mã hợp đồng" />
          </Form.Item>

          <Form.Item
            name="ma_khach_thue"
            label="Khách thuê"
            rules={[{ required: true, message: "Vui lòng chọn khách thuê" }]}
          >
            <Select
              showSearch
              placeholder="Chọn khách thuê"
              options={tenantOptions}
              optionFilterProp="label"
              onChange={handleTenantChange}
            />
          </Form.Item>

          {selectedTenant ? (
            <Descriptions bordered size="small" column={1} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Tên khách thuê">
                {pick(selectedTenant, ["ten_khach", "TENKHACH"])}
              </Descriptions.Item>
              <Descriptions.Item label="Số điện thoại">
                {pick(selectedTenant, ["so_dien_thoai", "SDT"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Email">
                {pick(selectedTenant, ["email", "EMAIL"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Trạng thái">
                {pick(selectedTenant, ["trang_thai", "TRANGTHAI"])}
              </Descriptions.Item>
            </Descriptions>
          ) : null}

          <Form.Item
            name="ma_yeu_cau"
            label="Yêu cầu thuê thêm nếu có"
            tooltip={
              selectedTenant
                ? "Chỉ hiện yêu cầu đã được BQL duyệt và chờ số hóa hợp đồng"
                : "Vui lòng chọn khách thuê trước"
            }
          >
            <Select
              allowClear
              showSearch
              placeholder={
                !selectedTenant
                  ? "Chọn khách thuê trước"
                  : rentRequests.length === 0
                    ? "Khách thuê này chưa có yêu cầu thuê thêm chờ số hóa"
                    : "Chọn yêu cầu thuê thêm"
              }
              disabled={!selectedTenant || rentRequests.length === 0}
              loading={loadingRentRequests}
              options={rentRequestOptions}
              optionFilterProp="label"
              onChange={handleRentRequestChange}
            />
          </Form.Item>

          {selectedRentRequest ? (
            <Descriptions bordered size="small" column={1} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Mã yêu cầu">
                {getRentRequestId(selectedRentRequest)}
              </Descriptions.Item>
              <Descriptions.Item label="Lý do">
                {pick(selectedRentRequest, ["ly_do", "LYDO"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Trạng thái yêu cầu">
                {pick(selectedRentRequest, ["trang_thai", "TRANGTHAI"])}
              </Descriptions.Item>
              <Descriptions.Item label="Mặt bằng từ yêu cầu">
                {getPremiseId(selectedRentRequest)}
              </Descriptions.Item>
            </Descriptions>
          ) : null}

          <Form.Item
            name="ma_mat_bang"
            label="Mặt bằng"
            rules={[{ required: true, message: "Vui lòng chọn mặt bằng" }]}
          >
            <Select
              showSearch
              placeholder={
                selectedRentRequest
                  ? "Tự động lấy theo yêu cầu thuê thêm"
                  : "Chọn mặt bằng còn trống"
              }
              disabled={Boolean(selectedRentRequest)}
              options={vacantPremiseOptions}
              optionFilterProp="label"
              onChange={handlePremiseChange}
            />
          </Form.Item>

          {selectedPremise ? (
            <Descriptions bordered size="small" column={1} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Mã mặt bằng">
                {getPremiseId(selectedPremise)}
              </Descriptions.Item>
              <Descriptions.Item label="Vị trí">
                {pick(selectedPremise, ["vi_tri", "VITRI"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Tầng">
                {pick(selectedPremise, ["tang", "TANG"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Diện tích">
                {pick(selectedPremise, ["dien_tich", "DIENTICH"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Loại mặt bằng">
                {pick(selectedPremise, ["loai_mat_bang", "LOAIMB"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Trạng thái">
                {pick(
                  selectedPremise,
                  ["trang_thai", "trang_thai_mat_bang", "TRANGTHAI"],
                  "-",
                )}
              </Descriptions.Item>
            </Descriptions>
          ) : null}

          <Form.Item
            name="ngay_bat_dau"
            label="Ngày bắt đầu"
            rules={[{ required: true, message: "Vui lòng chọn ngày bắt đầu" }]}
          >
            <DatePicker style={{ width: "100%" }} format="DD/MM/YYYY" />
          </Form.Item>

          <Form.Item
            name="ngay_ket_thuc"
            label="Ngày kết thúc"
            rules={[{ required: true, message: "Vui lòng chọn ngày kết thúc" }]}
          >
            <DatePicker style={{ width: "100%" }} format="DD/MM/YYYY" />
          </Form.Item>

          <Form.Item
            name="gia_thue_thang"
            label="Giá thuê tháng"
            rules={[{ required: true, message: "Vui lòng nhập giá thuê tháng" }]}
          >
            <InputNumber
              min={0}
              style={{ width: "100%" }}
              formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}
              parser={(value) => value.replace(/\$\s?|(,*)/g, "")}
              placeholder="Nhập giá thuê tháng"
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
