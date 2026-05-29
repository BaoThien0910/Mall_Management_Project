import { PlusOutlined } from "@ant-design/icons";
import {
  Descriptions,
  Form,
  Input,
  Modal,
  Select,
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
import { scheduleService } from "../../services/maintenanceService";
import { lookupService } from "../../services/lookupService";
import { formatDate, pick, pickId, toArray } from "../../utils/data";

function getPremiseId(record) {
  return pick(record, ["ma_mat_bang", "ma_mb", "MAMB"], undefined);
}

function getEmployeeId(record) {
  return pick(record, ["ma_nhan_vien", "ma_nv", "MANV"], undefined);
}

function normalizeDateTimeLocal(value) {
  if (!value) return value;
  return value.length === 16 ? `${value}:00` : value;
}

export default function ScheduleListPage() {
  const { role } = useAuth();
  const canCreate = role === ROLE.TP_VHBT;

  const [open, setOpen] = useState(false);
  const [premises, setPremises] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [selectedPremise, setSelectedPremise] = useState(null);
  const [selectedEmployee, setSelectedEmployee] = useState(null);

  const [form] = Form.useForm();

  const fetcher = useCallback((params) => scheduleService.list(params), []);
  const { items, loading, reload } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const loadLookupData = useCallback(async () => {
    if (!canCreate) return;

    try {
      const [premiseData, employeeData] = await Promise.all([
        lookupService.maintenancePremises(),
        lookupService.vhbtEmployees(),
      ]);

      setPremises(toArray(premiseData));
      setEmployees(toArray(employeeData));
    } catch (error) {
      showApiError(error);
    }
  }, [canCreate]);

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
    setSelectedPremise(null);
    setSelectedEmployee(null);
    form.resetFields();
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

  const create = async () => {
    try {
      const values = await form.validateFields();

      await scheduleService.create({
        ...values,
        ngay_thuc_hien_du_kien: normalizeDateTimeLocal(
          values.ngay_thuc_hien_du_kien,
        ),
      });

      message.success("Đã lập lịch bảo trì");
      setOpen(false);
      form.resetFields();
      reload();
    } catch (error) {
      showApiError(error);
    }
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
      title: "Mã lịch",
      render: (_, record) =>
        pick(record, ["ma_lich_bao_tri", "ma_lich_bt", "MALICHBT"]),
    },
    {
      title: "Mặt bằng",
      render: (_, record) => pick(record, ["ma_mat_bang", "MAMB"]),
    },
    {
      title: "Nhân viên",
      render: (_, record) =>
        pick(record, ["ma_nhan_vien_thuc_hien", "MANV_THUCHIEN"]),
    },
    {
      title: "Ngày dự kiến",
      render: (_, record) =>
        formatDate(
          pick(record, ["ngay_thuc_hien_du_kien", "NGAYTHUCHIEN_DUKIEN"]),
        ),
    },
    {
      title: "Nội dung",
      render: (_, record) => pick(record, ["noi_dung", "NOIDUNG"]),
    },
    {
      title: "Trạng thái",
      render: (_, record) => (
        <StatusTag value={pick(record, ["trang_thai", "TRANGTHAI"])} />
      ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Lịch bảo trì"
        subtitle="Lập và theo dõi lịch bảo trì mặt bằng"
        actionText={canCreate ? "Lập lịch" : undefined}
        actionIcon={<PlusOutlined />}
        onAction={canCreate ? openCreate : undefined}
      />

      <ResponsiveTable
        rowKey={(record) =>
          pickId(record, ["ma_lich_bao_tri", "ma_lich_bt", "MALICHBT"])
        }
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title="Lập lịch bảo trì"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={create}
        destroyOnClose
        okText="Tạo lịch"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical">
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
            name="ma_nhan_vien_thuc_hien"
            label="Nhân viên thực hiện"
            rules={[
              { required: true, message: "Vui lòng chọn nhân viên thực hiện" },
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

          <Form.Item
            name="ngay_thuc_hien_du_kien"
            label="Ngày thực hiện dự kiến"
            rules={[
              {
                required: true,
                message: "Vui lòng chọn ngày thực hiện dự kiến",
              },
            ]}
          >
            <Input type="datetime-local" />
          </Form.Item>

          <Form.Item
            name="noi_dung"
            label="Nội dung bảo trì"
            rules={[
              { required: true, message: "Vui lòng nhập nội dung bảo trì" },
            ]}
          >
            <Input.TextArea rows={4} placeholder="Nhập nội dung bảo trì" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}