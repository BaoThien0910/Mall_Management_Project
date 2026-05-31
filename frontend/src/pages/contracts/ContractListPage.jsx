import { PlusOutlined } from "@ant-design/icons";
import {
  Descriptions,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  DatePicker,
  message,
} from "antd";
import { useCallback, useEffect, useMemo, useState } from "react";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import Toolbar from "../../components/common/Toolbar";
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

  const fetcher = useCallback((params) => contractService.list(params), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

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

  const handleSearch = () => {
    setParams({
      keyword: keyword || undefined,
      page: 1,
      page_size: 20,
    });
  };

  const handleReload = () => {
    setKeyword("");
    setParams({ page: 1, page_size: 20 });
    reload();
  };

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
        onKeywordChange={setKeyword}
        placeholder="Tìm kiếm Mã HĐ, Khách thuê, Mặt bằng"
        onSearch={handleSearch}
        onReload={handleReload}
      />

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
