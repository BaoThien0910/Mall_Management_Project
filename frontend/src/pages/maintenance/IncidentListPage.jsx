import {
  CheckOutlined,
  PlusOutlined,
  ToolOutlined,
  UserAddOutlined,
} from "@ant-design/icons";
import {
  Button,
  Descriptions,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  message,
} from "antd";
import { useCallback, useEffect, useMemo, useState } from "react";

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
  { value: "Đã sửa chữa / thay thế xong", label: "Đã sửa chữa / thay thế xong" },
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

  const [form] = Form.useForm();
  const reviewResult = Form.useWatch("ket_qua", form);

  const fetcher = useCallback((params) => incidentService.list(params), []);
  const { items, loading, reload } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

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
      align: "right",
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

  return (
    <>
      <PageHeader
        title="Sự cố bảo trì"
        subtitle="Quản lý yêu cầu xử lý sự cố bảo trì"
        actionText={isTenant ? "Gửi sự cố" : undefined}
        actionIcon={<PlusOutlined />}
        onAction={isTenant ? openCreate : undefined}
      />

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