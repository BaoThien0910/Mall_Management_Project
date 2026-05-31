import { LockOutlined, PlusOutlined, UnlockOutlined, FilterOutlined } from "@ant-design/icons";
import {
  Button,
  Descriptions,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  message,
  Popover,
} from "antd";
import { useCallback, useEffect, useMemo, useState, useRef } from "react";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import Toolbar from "../../components/common/Toolbar";
import { ROLE, ROLE_LABEL } from "../../constants/roles";
import { useCrudList } from "../../hooks/useCrudList";
import { accountService } from "../../services/accountService";
import { showApiError } from "../../services/apiClient";
import { lookupService } from "../../services/lookupService";
import { pick, pickId, toArray } from "../../utils/data";

const ROLE_OPTIONS = Object.values(ROLE).map((value) => ({
  value,
  label: ROLE_LABEL[value],
}));

function getEmployeeId(record) {
  return pick(record, ["ma_nhan_vien", "ma_nv", "MANV"], undefined);
}

function getTenantId(record) {
  return pick(record, ["ma_khach_thue", "ma_kh", "MAKH"], undefined);
}

export default function AccountListPage() {
  const fetcher = useCallback((params) => accountService.list(params), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const [keyword, setKeyword] = useState("");
  const [popoverOpen, setPopoverOpen] = useState(false);
  const timerRef = useRef(null);

  const [appliedFilters, setAppliedFilters] = useState({
    ma_vai_tro: undefined,
  });

  const [tempMaVaiTro, setTempMaVaiTro] = useState(undefined);

  const applySearch = (val) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    timerRef.current = setTimeout(() => {
      const activeFilters = {};
      if (appliedFilters.ma_vai_tro) {
        activeFilters.ma_vai_tro = appliedFilters.ma_vai_tro;
      }
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
      ma_vai_tro: tempMaVaiTro,
    };
    setAppliedFilters(nextFilters);
    setPopoverOpen(false);

    setParams({
      keyword: keyword || undefined,
      ma_vai_tro: tempMaVaiTro || undefined,
      page: 1,
      page_size: 20,
    });
  };

  const handleCancel = () => {
    setTempMaVaiTro(appliedFilters.ma_vai_tro);
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempMaVaiTro(undefined);
    setAppliedFilters({
      ma_vai_tro: undefined,
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
      ma_vai_tro: undefined,
    });
    setTempMaVaiTro(undefined);
    setParams({
      page: 1,
      page_size: 20,
    });
    reload();
  };

  const activeFiltersCount = appliedFilters.ma_vai_tro ? 1 : 0;

  const filterContent = (
    <div style={{ padding: "8px", width: 280 }}>
      {/* Vai trò */}
      <div style={{ marginBottom: "20px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Vai trò</div>
        <Select
          placeholder="Chọn vai trò"
          value={tempMaVaiTro || undefined}
          onChange={setTempMaVaiTro}
          style={{ width: "100%" }}
          allowClear
          options={ROLE_OPTIONS}
        />
      </div>

      {/* Footer */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Button type="primary" danger onClick={handleClearFilters}>
          Xóa bộ lọc
        </Button>
        <Button type="primary" onClick={handleApply}>
          Áp dụng
        </Button>
      </div>
    </div>
  );
  const [open, setOpen] = useState(false);
  const [employees, setEmployees] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [selectedTenant, setSelectedTenant] = useState(null);

  const [form] = Form.useForm();
  const selectedRole = Form.useWatch("ma_vai_tro", form);

  const isTenantAccount = selectedRole === ROLE.KHACH_THUE;
  const isEmployeeAccount = selectedRole && selectedRole !== ROLE.KHACH_THUE;

  const loadLookupData = useCallback(async () => {
    try {
      const [employeeData, tenantData] = await Promise.all([
        lookupService.accountEmployees(),
        lookupService.accountTenants(),
      ]);

      setEmployees(toArray(employeeData));
      setTenants(toArray(tenantData));
    } catch (error) {
      showApiError(error);
    }
  }, []);

  useEffect(() => {
    loadLookupData();
  }, [loadLookupData]);

  const employeeOptions = useMemo(
    () =>
      employees
        .map((item) => {
          const value = getEmployeeId(item);
          return {
            value,
            label:
              item.label ||
              `${value} - ${pick(item, ["ho_ten", "HOTEN"])} - ${pick(
                item,
                ["phong_ban", "PHONGBAN"],
              )}`,
          };
        })
        .filter((item) => item.value),
    [employees],
  );

  const tenantOptions = useMemo(
    () =>
      tenants
        .map((item) => {
          const value = getTenantId(item);
          return {
            value,
            label: item.label || `${value} - ${pick(item, ["ten_khach", "TENKHACH"])}`,
          };
        })
        .filter((item) => item.value),
    [tenants],
  );

  const openCreateModal = () => {
    form.resetFields();
    setSelectedEmployee(null);
    setSelectedTenant(null);
    setOpen(true);
    loadLookupData();
  };

  const handleRoleChange = () => {
    form.setFieldsValue({
      ma_nhan_vien: undefined,
      ma_khach_thue: undefined,
    });
    setSelectedEmployee(null);
    setSelectedTenant(null);
  };

  const handleEmployeeChange = (value) => {
    const found = employees.find((item) => getEmployeeId(item) === value);
    setSelectedEmployee(found || null);
  };

  const handleTenantChange = (value) => {
    const found = tenants.find((item) => getTenantId(item) === value);
    setSelectedTenant(found || null);
  };

  const create = async () => {
    try {
      const values = await form.validateFields();

      const payload = {
        ten_dang_nhap: values.ten_dang_nhap,
        mat_khau_tam: values.mat_khau_tam,
        ma_vai_tro: values.ma_vai_tro,
        ma_nhan_vien: isEmployeeAccount ? values.ma_nhan_vien : null,
        ma_khach_thue: isTenantAccount ? values.ma_khach_thue : null,
      };

      await accountService.create(payload);

      message.success("Tạo tài khoản thành công");
      setOpen(false);
      form.resetFields();
      setSelectedEmployee(null);
      setSelectedTenant(null);
      reload();
      loadLookupData();
    } catch (error) {
      showApiError(error);
    }
  };

  const disable = async (row) => {
    try {
      const id = pickId(row, ["ma_tai_khoan", "ma_tk", "MATK"]);
      await accountService.disable(id, {
        ly_do: "Vô hiệu hóa từ giao diện quản trị",
      });
      message.success("Đã vô hiệu hóa tài khoản");
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const enable = async (row) => {
    try {
      const id = pickId(row, ["ma_tai_khoan", "ma_tk", "MATK"]);
      await accountService.enable(id, {
        ly_do: "Khôi phục từ giao diện quản trị",
      });
      message.success("Đã khôi phục tài khoản");
      reload();
    } catch (error) {
      showApiError(error);
    }
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
        <Descriptions.Item label="Mã nhân viên">
          {getEmployeeId(selectedEmployee)}
        </Descriptions.Item>
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
        <Descriptions.Item label="Trạng thái">
          <StatusTag value={pick(selectedEmployee, ["trang_thai", "TRANGTHAI"])} />
        </Descriptions.Item>
      </Descriptions>
    );
  };

  const renderSelectedTenant = () => {
    if (!selectedTenant) return null;

    return (
      <Descriptions
        bordered
        size="small"
        column={1}
        style={{ marginBottom: 16 }}
      >
        <Descriptions.Item label="Mã khách thuê">
          {getTenantId(selectedTenant)}
        </Descriptions.Item>
        <Descriptions.Item label="Tên khách thuê">
          {pick(selectedTenant, ["ten_khach", "TENKHACH"])}
        </Descriptions.Item>
        <Descriptions.Item label="CCCD/MST">
          {pick(selectedTenant, ["cccd_mst", "CCCD_MST"])}
        </Descriptions.Item>
        <Descriptions.Item label="Số điện thoại">
          {pick(selectedTenant, ["so_dien_thoai", "SDT"], "-")}
        </Descriptions.Item>
        <Descriptions.Item label="Email">
          {pick(selectedTenant, ["email", "EMAIL"], "-")}
        </Descriptions.Item>
        <Descriptions.Item label="Địa chỉ">
          {pick(selectedTenant, ["dia_chi", "DIACHI"], "-")}
        </Descriptions.Item>
        <Descriptions.Item label="Trạng thái">
          <StatusTag value={pick(selectedTenant, ["trang_thai", "TRANGTHAI"])} />
        </Descriptions.Item>
      </Descriptions>
    );
  };

  const columns = [
    {
      title: "Tên người dùng",
      render: (_, record) =>
        pick(record, ["ten_dang_nhap", "username", "TENDANGNHAP"]),
    },
    {
      title: "Mã tài khoản",
      render: (_, record) =>
        pick(record, ["ma_tai_khoan", "ma_tk", "MATK"]),
    },
    {
      title: "Vai trò",
      render: (_, record) => {
        const roleCode = pick(record, ["ma_vai_tro", "MAVAITRO"]);
        return ROLE_LABEL[roleCode] || roleCode;
      },
    },
    {
      title: "Nhân viên / Khách thuê",
      render: (_, record) => {
        const employeeId = pick(record, ["ma_nhan_vien", "ma_nv", "MANV"], "");
        const tenantId = pick(record, ["ma_khach_thue", "ma_kh", "MAKH"], "");

        return employeeId || tenantId || "-";
      },
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
        const isActive = pick(record, ["trang_thai", "TRANGTHAI"]) === "Hoạt động";

        return (
          <Space>
            {isActive ? (
              <Popconfirm
                title="Vô hiệu hóa tài khoản này?"
                okText="Vô hiệu hóa"
                cancelText="Hủy"
                onConfirm={() => disable(record)}
              >
                <Button size="small" danger icon={<LockOutlined />}>
                  Vô hiệu
                </Button>
              </Popconfirm>
            ) : (
              <Popconfirm
                title="Khôi phục tài khoản này?"
                okText="Khôi phục"
                cancelText="Hủy"
                onConfirm={() => enable(record)}
              >
                <Button size="small" icon={<UnlockOutlined />}>
                  Khôi phục
                </Button>
              </Popconfirm>
            )}
          </Space>
        );
      },
    },
  ];

  return (
    <>
      <PageHeader
        title="Quản lý tài khoản"
        subtitle="Tạo, vô hiệu hóa và khôi phục tài khoản người dùng"
        actionText="Thêm tài khoản"
        actionIcon={<PlusOutlined />}
        onAction={openCreateModal}
      />

      <Toolbar
        keyword={keyword}
        onKeywordChange={(val) => {
          setKeyword(val);
          applySearch(val);
        }}
        placeholder="Tìm kiếm tên người dùng"
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
        rowKey={(record) => pickId(record, ["ma_tai_khoan", "ma_tk", "MATK"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title="Tạo tài khoản"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={create}
        destroyOnClose
        okText="Tạo tài khoản"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="ten_dang_nhap"
            label="Tên đăng nhập"
            rules={[
              { required: true, message: "Vui lòng nhập tên đăng nhập" },
              { max: 50, message: "Tên đăng nhập tối đa 50 ký tự" },
            ]}
          >
            <Input placeholder="Nhập tên đăng nhập" />
          </Form.Item>

          <Form.Item
            name="mat_khau_tam"
            label="Mật khẩu tạm"
            rules={[
              { required: true, message: "Vui lòng nhập mật khẩu tạm" },
              { min: 8, message: "Mật khẩu tối thiểu 8 ký tự" },
            ]}
          >
            <Input.Password placeholder="Nhập mật khẩu tạm" />
          </Form.Item>

          <Form.Item
            name="ma_vai_tro"
            label="Vai trò"
            rules={[{ required: true, message: "Vui lòng chọn vai trò" }]}
          >
            <Select
              showSearch
              placeholder="Chọn vai trò"
              options={ROLE_OPTIONS}
              optionFilterProp="label"
              onChange={handleRoleChange}
            />
          </Form.Item>

          {isEmployeeAccount ? (
            <>
              <Form.Item
                name="ma_nhan_vien"
                label="Nhân viên"
                rules={[{ required: true, message: "Vui lòng chọn nhân viên" }]}
              >
                <Select
                  showSearch
                  placeholder="Chọn nhân viên từ database"
                  options={employeeOptions}
                  optionFilterProp="label"
                  onChange={handleEmployeeChange}
                />
              </Form.Item>

              {renderSelectedEmployee()}
            </>
          ) : null}

          {isTenantAccount ? (
            <>
              <Form.Item
                name="ma_khach_thue"
                label="Khách thuê"
                rules={[{ required: true, message: "Vui lòng chọn khách thuê" }]}
              >
                <Select
                  showSearch
                  placeholder="Chọn khách thuê từ database"
                  options={tenantOptions}
                  optionFilterProp="label"
                  onChange={handleTenantChange}
                />
              </Form.Item>

              {renderSelectedTenant()}
            </>
          ) : null}
        </Form>
      </Modal>
    </>
  );
}