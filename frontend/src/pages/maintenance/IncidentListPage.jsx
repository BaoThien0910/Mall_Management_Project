import {
  CheckOutlined,
  FilterOutlined,
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
  ToolOutlined,
  UserAddOutlined,
} from "@ant-design/icons";
import {
  Button,
  Card,
  Checkbox,
  DatePicker,
  Descriptions,
  Form,
  Input,
  InputNumber,
  Modal,
  Popover,
  Select,
  Space,
  message,
} from "antd";
import dayjs from "dayjs";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { useCrudList } from "../../hooks/useCrudList";
import { showApiError } from "../../services/apiClient";
import { incidentService } from "../../services/maintenanceService";
import { lookupService } from "../../services/lookupService";
import { formatDate, pick, pickId, toArray } from "../../utils/data";

const REVIEW_OPTIONS = [
  { value: "DUYET", label: "Duyệt" },
  { value: "TU_CHOI", label: "Từ chối" },
];

const INCIDENT_RESULT_OPTIONS = [
  { value: "Đã xử lý xong", label: "Đã xử lý xong" },
  { value: "Không phát hiện lỗi", label: "Không phát hiện lỗi" },
  {
    value: "Không thể xử lý do ngoài phạm vi bảo trì",
    label: "Không thể xử lý do ngoài phạm vi bảo trì",
  },
];

function getNowLocalDateTimeString() {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 19);
}

function getPremiseId(record) {
  return pick(record, ["ma_mat_bang", "ma_mb", "MAMB"], undefined);
}

function getEmployeeId(record) {
  return pick(record, ["ma_nhan_vien", "ma_nv", "MANV"], undefined);
}

export default function IncidentListPage() {
  const { role, user } = useAuth();

  const isTenant = role === ROLE.KHACH_THUE;
  const isManager = role === ROLE.BQL;
  const isMaintenanceLeader = role === ROLE.TP_VHBT;
  const isMaintenanceStaff = [ROLE.TP_VHBT, ROLE.NV_VHBT].includes(role);

  const [open, setOpen] = useState(false);
  const [action, setAction] = useState(null);
  const [row, setRow] = useState(null);
  const [premises, setPremises] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [selectedPremise, setSelectedPremise] = useState(null);
  const [selectedEmployee, setSelectedEmployee] = useState(null);

  const [keyword, setKeyword] = useState("");
  const [popoverOpen, setPopoverOpen] = useState(false);
  const [tuNgay, setTuNgay] = useState("");
  const [denNgay, setDenNgay] = useState("");
  const [trangThaiList, setTrangThaiList] = useState([]);

  const [tempTuNgay, setTempTuNgay] = useState("");
  const [tempDenNgay, setTempDenNgay] = useState("");
  const [tempTrangThaiList, setTempTrangThaiList] = useState([]);

  const timerRef = useRef(null);

  const [form] = Form.useForm();
  const reviewResult = Form.useWatch("ket_qua", form);

  const fetcher = useCallback((params) => incidentService.list(params), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const applyFilters = (updates, immediate = false) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    const run = () => {
      const nextFilters = {
        keyword: keyword || undefined,
        tu_ngay: tuNgay ? `${tuNgay}T00:00:00` : undefined,
        den_ngay: denNgay ? `${denNgay}T23:59:59` : undefined,
        trang_thai: trangThaiList.length ? trangThaiList.join(",") : undefined,
        ...updates
      };

      const cleanParams = {};
      Object.keys(nextFilters).forEach(key => {
        if (nextFilters[key] !== undefined && nextFilters[key] !== null && nextFilters[key] !== "") {
          cleanParams[key] = nextFilters[key];
        }
      });

      setParams({
        ...cleanParams,
        page: 1,
        page_size: 20,
      });
    };

    if (immediate) {
      run();
    } else {
      timerRef.current = setTimeout(run, 500);
    }
  };

  const handleKeywordSearch = () => {
    applyFilters({ keyword: keyword || undefined }, true);
  };

  const handleOpenPopover = (visible) => {
    if (visible) {
      setTempTuNgay(tuNgay);
      setTempDenNgay(denNgay);
      setTempTrangThaiList(trangThaiList);
    }
    setPopoverOpen(visible);
  };

  const handleApply = () => {
    setTuNgay(tempTuNgay);
    setDenNgay(tempDenNgay);
    setTrangThaiList(tempTrangThaiList);
    setPopoverOpen(false);

    applyFilters({
      tu_ngay: tempTuNgay ? `${tempTuNgay}T00:00:00` : undefined,
      den_ngay: tempDenNgay ? `${tempDenNgay}T23:59:59` : undefined,
      trang_thai: tempTrangThaiList.length ? tempTrangThaiList.join(",") : undefined,
    }, true);
  };

  const handleCancel = () => {
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempTuNgay("");
    setTempDenNgay("");
    setTempTrangThaiList([]);
    setTuNgay("");
    setDenNgay("");
    setTrangThaiList([]);
    setPopoverOpen(false);

    applyFilters({
      tu_ngay: undefined,
      den_ngay: undefined,
      trang_thai: undefined,
    }, true);
  };

  const handleReload = () => {
    reload();
  };

  const currentEmployeeId = pick(
    user,
    ["ma_nhan_vien", "ma_nv", "MANV"],
    undefined,
  );

  const loadLookupData = useCallback(async () => {
    try {
      const premiseData = await lookupService.maintenancePremises();
      setPremises(toArray(premiseData));

      if (isMaintenanceStaff) {
        const employeeData = await lookupService.vhbtEmployees();
        setEmployees(toArray(employeeData));
      }
    } catch (error) {
      showApiError(error);
    }
  }, [isMaintenanceStaff]);

  useEffect(() => {
    loadLookupData();
  }, [loadLookupData]);

  const premiseOptions = useMemo(
    () =>
      premises.map((item) => {
        const value = getPremiseId(item);
        return {
          value,
          label:
            item.label ||
            `${value} - ${pick(item, ["vi_tri", "VITRI"])} - Tầng ${pick(
              item,
              ["tang", "TANG"],
            )}`,
        };
      }),
    [premises],
  );

  const employeeOptions = useMemo(
    () =>
      employees.map((item) => {
        const value = getEmployeeId(item);
        return {
          value,
          label: item.label || `${value} - ${pick(item, ["ho_ten", "HOTEN"])}`,
        };
      }),
    [employees],
  );

  const openCreate = () => {
    setAction("create");
    setRow({});
    setSelectedPremise(null);
    setSelectedEmployee(null);
    form.resetFields();
    setOpen(true);
  };

  const openAction = (type, record) => {
    setAction(type);
    setRow(record);
    setSelectedPremise(null);
    setSelectedEmployee(null);
    form.resetFields();

    const initialValues = {};

    if (type === "review") {
      initialValues.ket_qua = "DUYET";
    }

    if (type === "assign") {
      initialValues.ma_nhan_vien_phan_cong = currentEmployeeId;
    }

    if (type === "result") {
      initialValues.ket_qua = INCIDENT_RESULT_OPTIONS[0].value;
    }

    form.setFieldsValue(initialValues);
    setOpen(true);
  };

  const handlePremiseChange = (value) => {
    const found = premises.find((item) => getPremiseId(item) === value);
    setSelectedPremise(found || null);
  };

  const handleEmployeeChange = (value) => {
    const found = employees.find((item) => getEmployeeId(item) === value);
    setSelectedEmployee(found || null);
  };

  const submit = async () => {
    const incidentId = pickId(row, ["ma_su_co", "MASUCO"]);

    try {
      const values = await form.validateFields();

      if (action === "create") {
        await incidentService.create(values);
      }

      if (action === "review") {
        await incidentService.review(incidentId, {
          ket_qua: values.ket_qua,
          ly_do_tu_choi:
            values.ket_qua === "TU_CHOI" ? values.ly_do_tu_choi : undefined,
        });
      }

      if (action === "assign") {
        await incidentService.assign(incidentId, {
          ma_nhan_vien_phan_cong:
            values.ma_nhan_vien_phan_cong || currentEmployeeId,
          ma_nhan_vien_xu_ly: values.ma_nhan_vien_xu_ly,
          ghi_chu: values.ghi_chu,
        });
      }

      if (action === "result") {
        await incidentService.updateResult(incidentId, {
          ket_qua: values.ket_qua,
          ngay_hoan_thanh: getNowLocalDateTimeString(),
        });
      }

      if (action === "cost") {
        await incidentService.updateCost(incidentId, {
          chi_phi: values.chi_phi,
        });
      }

      message.success("Thao tác thành công");
      setOpen(false);
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const renderIncidentSummary = () => {
    if (!row || action === "create") return null;

    return (
      <Descriptions
        bordered
        size="small"
        column={1}
        style={{ marginBottom: 16 }}
      >
        <Descriptions.Item label="Mã sự cố">
          {pick(row, ["ma_su_co", "MASUCO"])}
        </Descriptions.Item>
        <Descriptions.Item label="Mặt bằng">
          {pick(row, ["ma_mat_bang", "MAMB"])}
        </Descriptions.Item>
        <Descriptions.Item label="Khách thuê">
          {pick(row, ["ma_khach_thue", "MAKH"])}
        </Descriptions.Item>
        <Descriptions.Item label="Ngày gửi">
          {formatDate(pick(row, ["ngay_gui", "NGAYGUI"]))}
        </Descriptions.Item>
        <Descriptions.Item label="Trạng thái">
          <StatusTag value={pick(row, ["trang_thai", "TRANGTHAI"])} />
        </Descriptions.Item>
        <Descriptions.Item label="Mô tả">
          {pick(row, ["mo_ta", "MOTA"])}
        </Descriptions.Item>
      </Descriptions>
    );
  };

  const renderSelectedPremise = () => {
    if (!selectedPremise) return null;

    return (
      <Descriptions
        bordered
        size="small"
        column={1}
        style={{ marginBottom: 16 }}
      >
        <Descriptions.Item label="Vị trí">
          {pick(selectedPremise, ["vi_tri", "VITRI"])}
        </Descriptions.Item>
        <Descriptions.Item label="Tầng">
          {pick(selectedPremise, ["tang", "TANG"])}
        </Descriptions.Item>
        <Descriptions.Item label="Diện tích">
          {pick(selectedPremise, ["dien_tich", "DIENTICH"])}
        </Descriptions.Item>
        <Descriptions.Item label="Loại mặt bằng">
          {pick(selectedPremise, ["loai_mat_bang", "LOAIMB"])}
        </Descriptions.Item>
        <Descriptions.Item label="Trạng thái">
          <StatusTag value={pick(selectedPremise, ["trang_thai", "TRANGTHAI"])} />
        </Descriptions.Item>
      </Descriptions>
    );
  };

  const renderSelectedEmployee = () => {
    if (!selectedEmployee) return null;

    return (
      <Descriptions
        bordered
        size="small"
        column={1}
        style={{ marginBottom: 16 }}
      >
        <Descriptions.Item label="Họ tên">
          {pick(selectedEmployee, ["ho_ten", "HOTEN"])}
        </Descriptions.Item>
        <Descriptions.Item label="Phòng ban">
          {pick(selectedEmployee, ["phong_ban", "PHONGBAN"])}
        </Descriptions.Item>
        <Descriptions.Item label="Chức vụ">
          {pick(selectedEmployee, ["chuc_vu", "CHUCVU"])}
        </Descriptions.Item>
        <Descriptions.Item label="Số điện thoại">
          {pick(selectedEmployee, ["so_dien_thoai", "SDT"], "-")}
        </Descriptions.Item>
        <Descriptions.Item label="Email">
          {pick(selectedEmployee, ["email", "EMAIL"], "-")}
        </Descriptions.Item>
      </Descriptions>
    );
  };

  const columns = [
    {
      title: "Mã sự cố",
      render: (_, record) => pick(record, ["ma_su_co", "MASUCO"]),
    },
    {
      title: "Mặt bằng",
      render: (_, record) => pick(record, ["ma_mat_bang", "MAMB"]),
    },
    {
      title: "Khách thuê",
      render: (_, record) => pick(record, ["ma_khach_thue", "MAKH"]),
    },
    {
      title: "Mô tả",
      render: (_, record) => pick(record, ["mo_ta", "MOTA"]),
    },
    {
      title: "Ngày gửi",
      render: (_, record) => formatDate(pick(record, ["ngay_gui", "NGAYGUI"])),
    },
    {
      title: "Trạng thái",
      render: (_, record) => (
        <StatusTag value={pick(record, ["trang_thai", "TRANGTHAI"])} />
      ),
    },
    {
      title: "Thao tác",
      render: (_, record) => {
        const status = pick(record, ["trang_thai", "TRANGTHAI"]);

        return (
          <Space wrap>
            {isManager && status === "Chờ duyệt" ? (
              <Button
                size="small"
                icon={<CheckOutlined />}
                onClick={() => openAction("review", record)}
              >
                Duyệt
              </Button>
            ) : null}

            {isMaintenanceLeader && status === "Đã duyệt" ? (
              <Button
                size="small"
                icon={<UserAddOutlined />}
                onClick={() => openAction("assign", record)}
              >
                Phân công
              </Button>
            ) : null}

            {isMaintenanceStaff && status === "Đang xử lý" ? (
              <Button
                size="small"
                icon={<ToolOutlined />}
                onClick={() => openAction("result", record)}
              >
                Kết quả
              </Button>
            ) : null}

            {isMaintenanceStaff &&
            ["Đang xử lý", "Hoàn thành"].includes(status) ? (
              <Button size="small" onClick={() => openAction("cost", record)}>
                Chi phí
              </Button>
            ) : null}
          </Space>
        );
      },
    },
  ];

  const modalTitle = {
    create: "Gửi sự cố bảo trì",
    review: "Duyệt sự cố",
    assign: "Phân công xử lý",
    result: "Cập nhật kết quả",
    cost: "Nhập chi phí",
  }[action];

  const activeFiltersCount = (tuNgay ? 1 : 0) + (denNgay ? 1 : 0) + (trangThaiList.length ? 1 : 0);

  const filterContent = (
    <div style={{ padding: "8px", width: 440 }}>
      {/* Ngày gửi */}
      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Ngày gửi</div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ color: "#555" }}>From:</span>
          <DatePicker
            value={tempTuNgay ? dayjs(tempTuNgay) : null}
            onChange={(date) => setTempTuNgay(date ? dayjs(date).format("YYYY-MM-DD") : "")}
            format="DD/MM/YYYY"
            placeholder="Từ ngày"
            style={{ width: "100%" }}
            allowClear={false}
          />
          <span style={{ color: "#bfbfbf" }}>-</span>
          <span style={{ color: "#555" }}>To:</span>
          <DatePicker
            value={tempDenNgay ? dayjs(tempDenNgay) : null}
            onChange={(date) => setTempDenNgay(date ? dayjs(date).format("YYYY-MM-DD") : "")}
            format="DD/MM/YYYY"
            placeholder="Đến ngày"
            style={{ width: "100%" }}
            allowClear={false}
          />
        </div>
      </div>

      {/* Trạng thái */}
      <div style={{ marginBottom: "20px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Trạng thái</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "12px" }}>
          {["Chờ duyệt", "Đã duyệt", "Từ chối", "Đang xử lý", "Hoàn thành"].map((status) => {
            const checked = tempTrangThaiList.includes(status);
            return (
              <Checkbox
                key={status}
                checked={checked}
                onChange={(e) => {
                  const next = e.target.checked
                    ? [...tempTrangThaiList, status]
                    : tempTrangThaiList.filter((s) => s !== status);
                  setTempTrangThaiList(next);
                }}
              >
                {status}
              </Checkbox>
            );
          })}
        </div>
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

  return (
    <>
      <PageHeader
        title="Sự cố bảo trì"
        subtitle="Quản lý yêu cầu xử lý sự cố bảo trì"
        actionText={isTenant ? "Gửi sự cố" : undefined}
        actionIcon={<PlusOutlined />}
        onAction={isTenant ? openCreate : undefined}
      />

      <Card
        className="toolbar-card"
        bordered={false}
        style={{ marginBottom: "16px" }}
        styles={{ body: { padding: "16px" } }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Input
            allowClear
            prefix={<SearchOutlined />}
            placeholder="Tìm kiếm mã Mặt bằng, Khách thuê"
            value={keyword}
            onChange={(e) => {
              const val = e.target.value;
              setKeyword(val);
              applyFilters({ keyword: val || undefined }, !val);
            }}
            onPressEnter={handleKeywordSearch}
            style={{ width: 340 }}
          />

          <Button icon={<ReloadOutlined />} onClick={handleReload} style={{ minWidth: 100 }}>
            Tải lại
          </Button>

          <Popover
            content={filterContent}
            title="Bộ lọc"
            trigger="click"
            open={popoverOpen}
            onOpenChange={handleOpenPopover}
            placement="bottomLeft"
            overlayStyle={{ zIndex: 1050 }}
          >
            <Button
              type="primary"
              icon={<FilterOutlined />}
              style={{
                display: "inline-flex",
                alignItems: "center",
                minWidth: 100,
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
        </div>
      </Card>

      <ResponsiveTable
        rowKey={(record) => pickId(record, ["ma_su_co", "MASUCO"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title={modalTitle}
        open={open}
        onCancel={() => setOpen(false)}
        onOk={submit}
        destroyOnClose
        okText="Lưu"
        cancelText="Hủy"
      >
        {renderIncidentSummary()}

        <Form form={form} layout="vertical">
          {action === "create" ? (
            <>
              <Form.Item
                name="ma_mat_bang"
                label="Mặt bằng"
                rules={[{ required: true, message: "Vui lòng chọn mặt bằng" }]}
              >
                <Select
                  showSearch
                  placeholder="Chọn mặt bằng"
                  options={premiseOptions}
                  optionFilterProp="label"
                  onChange={handlePremiseChange}
                />
              </Form.Item>

              {renderSelectedPremise()}

              <Form.Item
                name="mo_ta"
                label="Mô tả sự cố"
                rules={[{ required: true, message: "Vui lòng nhập mô tả sự cố" }]}
              >
                <Input.TextArea rows={4} placeholder="Nhập nội dung sự cố" />
              </Form.Item>
            </>
          ) : null}

          {action === "review" ? (
            <>
              <Form.Item
                name="ket_qua"
                label="Kết quả duyệt"
                rules={[{ required: true, message: "Vui lòng chọn kết quả duyệt" }]}
              >
                <Select options={REVIEW_OPTIONS} />
              </Form.Item>

              {reviewResult === "TU_CHOI" ? (
                <Form.Item
                  name="ly_do_tu_choi"
                  label="Lý do từ chối"
                  rules={[
                    {
                      required: true,
                      message: "Vui lòng nhập lý do từ chối",
                    },
                  ]}
                >
                  <Input.TextArea rows={3} placeholder="Nhập lý do từ chối" />
                </Form.Item>
              ) : null}
            </>
          ) : null}

          {action === "assign" ? (
            <>
              <Form.Item name="ma_nhan_vien_phan_cong" hidden>
                <Input />
              </Form.Item>

              <Form.Item
                name="ma_nhan_vien_xu_ly"
                label="Nhân viên xử lý"
                rules={[
                  { required: true, message: "Vui lòng chọn nhân viên xử lý" },
                ]}
              >
                <Select
                  showSearch
                  placeholder="Chọn nhân viên Vận hành - Bảo trì"
                  options={employeeOptions}
                  optionFilterProp="label"
                  onChange={handleEmployeeChange}
                />
              </Form.Item>

              {renderSelectedEmployee()}

              <Form.Item name="ghi_chu" label="Ghi chú">
                <Input.TextArea rows={3} placeholder="Nhập ghi chú nếu có" />
              </Form.Item>
            </>
          ) : null}

          {action === "result" ? (
            <Form.Item
              name="ket_qua"
              label="Kết quả xử lý"
              rules={[{ required: true, message: "Vui lòng chọn kết quả xử lý" }]}
            >
              <Select options={INCIDENT_RESULT_OPTIONS} />
            </Form.Item>
          ) : null}

          {action === "cost" ? (
            <Form.Item
              name="chi_phi"
              label="Chi phí"
              rules={[{ required: true, message: "Vui lòng nhập chi phí" }]}
            >
              <InputNumber
                min={0}
                style={{ width: "100%" }}
                placeholder="Nhập chi phí"
              />
            </Form.Item>
          ) : null}
        </Form>
      </Modal>
    </>
  );
}