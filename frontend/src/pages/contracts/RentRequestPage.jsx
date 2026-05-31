import { CheckOutlined, CloseOutlined, PlusOutlined, FilterOutlined, ReloadOutlined, SearchOutlined } from "@ant-design/icons";
import {
  Button,
  Descriptions,
  Form,
  Input,
  Modal,
  Select,
  Space,
  message,
  Popover,
  DatePicker,
} from "antd";
import { useCallback, useEffect, useState, useRef } from "react";
import dayjs from "dayjs";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import Toolbar from "../../components/common/Toolbar";
import { ROLE } from "../../constants/roles";
import { YEU_CAU_THUE_THEM_STATUS } from "../../constants/statuses";
import { useAuth } from "../../hooks/useAuth";
import { useCrudList } from "../../hooks/useCrudList";
import { rentRequestService } from "../../services/rentRequestService";
import { lookupService } from "../../services/lookupService";
import { showApiError } from "../../services/apiClient";
import { pick, pickId, formatDate, toArray } from "../../utils/data";

function getPremiseId(record) {
  return pick(record, ["ma_mat_bang", "ma_mb", "MAMB"], undefined);
}

export default function RentRequestPage() {
  const { role } = useAuth();
  const isTenant = role === ROLE.KHACH_THUE;

  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();
  const [vacantPremises, setVacantPremises] = useState([]);
  const [selectedPremise, setSelectedPremise] = useState(null);

  // Search and Filter states
  const [keyword, setKeyword] = useState("");
  const [popoverOpen, setPopoverOpen] = useState(false);
  const timerRef = useRef(null);

  const [appliedFilters, setAppliedFilters] = useState({
    trang_thai: undefined,
    ngay_gui_tu: undefined,
    ngay_gui_den: undefined,
  });

  const [tempNgayGuiTu, setTempNgayGuiTu] = useState("");
  const [tempNgayGuiDen, setTempNgayGuiDen] = useState("");
  const [tempTrangThai, setTempTrangThai] = useState(undefined);

  const fetcher = useCallback(
    (params) => (isTenant ? rentRequestService.myRequests(params) : rentRequestService.list(params)),
    [isTenant],
  );

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
      trang_thai: tempTrangThai,
      ngay_gui_tu: tempNgayGuiTu,
      ngay_gui_den: tempNgayGuiDen,
    };
    setAppliedFilters(nextFilters);
    setPopoverOpen(false);

    const activeFilters = {};
    Object.keys(nextFilters).forEach((key) => {
      if (nextFilters[key] !== undefined && nextFilters[key] !== null && nextFilters[key] !== "") {
        activeFilters[key] = nextFilters[key];
      }
    });

    setParams({
      keyword: keyword || undefined,
      ...activeFilters,
      page: 1,
      page_size: 20,
    });
  };

  const handleCancel = () => {
    setTempNgayGuiTu(appliedFilters.ngay_gui_tu || "");
    setTempNgayGuiDen(appliedFilters.ngay_gui_den || "");
    setTempTrangThai(appliedFilters.trang_thai);
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempNgayGuiTu("");
    setTempNgayGuiDen("");
    setTempTrangThai(undefined);

    setAppliedFilters({
      trang_thai: undefined,
      ngay_gui_tu: undefined,
      ngay_gui_den: undefined,
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
      ngay_gui_tu: undefined,
      ngay_gui_den: undefined,
    };
    setAppliedFilters(cleared);
    setTempNgayGuiTu("");
    setTempNgayGuiDen("");
    setTempTrangThai(undefined);
    setParams({
      page: 1,
      page_size: 20,
    });
    reload();
  };

  const activeFiltersCount =
    (appliedFilters.trang_thai ? 1 : 0) +
    (appliedFilters.ngay_gui_tu ? 1 : 0) +
    (appliedFilters.ngay_gui_den ? 1 : 0);

  const filterContent = (
    <div style={{ padding: "8px", width: 320 }}>
      {/* Ngày gửi */}
      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Ngày gửi</div>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ color: "#555", width: "40px" }}>Từ:</span>
            <DatePicker
              value={tempNgayGuiTu ? dayjs(tempNgayGuiTu) : null}
              onChange={(date) => setTempNgayGuiTu(date ? dayjs(date).format("YYYY-MM-DD") : "")}
              format="DD/MM/YYYY"
              placeholder="Từ ngày"
              style={{ width: "100%" }}
              allowClear={false}
            />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ color: "#555", width: "40px" }}>Đến:</span>
            <DatePicker
              value={tempNgayGuiDen ? dayjs(tempNgayGuiDen) : null}
              onChange={(date) => setTempNgayGuiDen(date ? dayjs(date).format("YYYY-MM-DD") : "")}
              format="DD/MM/YYYY"
              placeholder="Đến ngày"
              style={{ width: "100%" }}
              allowClear={false}
            />
          </div>
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
          options={YEU_CAU_THUE_THEM_STATUS.map((item) => ({ value: item, label: item }))}
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

  const loadVacantPremises = useCallback(async () => {
    try {
      const data = await lookupService.vacantPremises();
      setVacantPremises(toArray(data));
    } catch (error) {
      showApiError(error);
    }
  }, []);

  useEffect(() => {
    if (isTenant && open) {
      loadVacantPremises();
    }
  }, [isTenant, open, loadVacantPremises]);

  const openCreateModal = () => {
    form.resetFields();
    setSelectedPremise(null);
    setOpen(true);
  };

  const handlePremiseChange = (value) => {
    const premise = vacantPremises.find((item) => getPremiseId(item) === value);
    setSelectedPremise(premise || null);
  };

  const create = async () => {
    try {
      const values = await form.validateFields();

      await rentRequestService.create(values);

      message.success("Đã gửi yêu cầu thuê thêm");
      setOpen(false);
      form.resetFields();
      setSelectedPremise(null);
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const review = async (row, ketQua) => {
    try {
      const payload = { ket_qua: ketQua };

      if (ketQua === "TU_CHOI") {
        payload.ly_do_tu_choi = "Không đáp ứng điều kiện thuê thêm";
      } else {
        payload.ghi_chu_cho_kdtc = "Chuyển sang số hóa hợp đồng";
      }

      await rentRequestService.review(
        pickId(row, ["ma_yeu_cau", "ma_yc", "MAYC"]),
        payload,
      );

      message.success("Đã xử lý yêu cầu");
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const premiseOptions = vacantPremises
    .map((item) => {
      const value = getPremiseId(item);
      const viTri = pick(item, ["vi_tri", "VITRI"], "");
      const dienTich = pick(item, ["dien_tich", "DIENTICH"], "");
      const tang = pick(item, ["tang", "TANG"], "");

      return {
        value,
        label: `${value} - ${viTri} - Tầng ${tang} (${dienTich} m²)`,
      };
    })
    .filter((item) => item.value);

  const columns = [
    {
      title: "Mã YC",
      render: (_, record) => pick(record, ["ma_yeu_cau", "ma_yc", "MAYC"]),
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
      title: "Ngày gửi",
      render: (_, record) => formatDate(pick(record, ["ngay_gui", "NGAYGUI"])),
    },
    {
      title: "Lý do",
      render: (_, record) => pick(record, ["ly_do", "LYDO"]),
    },
    {
      title: "Trạng thái",
      render: (_, record) => <StatusTag value={pick(record, ["trang_thai", "TRANGTHAI"])} />,
    },
    {
      title: "Thao tác",
      align: "right",
      render: (_, record) =>
        !isTenant && pick(record, ["trang_thai", "TRANGTHAI"]) === "Chờ duyệt" ? (
          <Space>
            <Button
              size="small"
              icon={<CheckOutlined />}
              onClick={() => review(record, "DUYET")}
            >
              Duyệt
            </Button>
            <Button
              size="small"
              danger
              icon={<CloseOutlined />}
              onClick={() => review(record, "TU_CHOI")}
            >
              Từ chối
            </Button>
          </Space>
        ) : null,
    },
  ];

  return (
    <>
      <PageHeader
        title="Yêu cầu thuê thêm"
        subtitle="Gửi và theo dõi yêu cầu thuê thêm mặt bằng"
        actionText={isTenant ? "Gửi yêu cầu" : undefined}
        actionIcon={<PlusOutlined />}
        onAction={isTenant ? openCreateModal : undefined}
      />

      <Toolbar
        keyword={keyword}
        onKeywordChange={(val) => {
          setKeyword(val);
          applySearch(val);
        }}
        placeholder="Tìm kiếm mã Khách thuê, Mặt Bằng"
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
        rowKey={(record) => pickId(record, ["ma_yeu_cau", "ma_yc", "MAYC"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title="Gửi yêu cầu thuê thêm"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={create}
        destroyOnClose
        okText="Gửi yêu cầu"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="ma_mat_bang"
            label="Mặt bằng thuê thêm"
            rules={[{ required: true, message: "Vui lòng chọn mặt bằng thuê thêm" }]}
          >
            <Select
              showSearch
              placeholder="Chọn mặt bằng còn trống"
              optionFilterProp="label"
              onChange={handlePremiseChange}
              options={premiseOptions}
            />
          </Form.Item>

          {selectedPremise ? (
            <Descriptions bordered size="small" column={1} style={{ marginBottom: 16 }}>
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
                {pick(selectedPremise, ["trang_thai", "TRANGTHAI"], "-")}
              </Descriptions.Item>
            </Descriptions>
          ) : null}

          <Form.Item
            name="ly_do"
            label="Lý do thuê thêm"
            rules={[{ required: true, message: "Vui lòng nhập lý do thuê thêm" }]}
          >
            <Input.TextArea rows={4} placeholder="Nhập lý do thuê thêm" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
