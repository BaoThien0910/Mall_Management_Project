import { ThunderboltOutlined, FilterOutlined } from "@ant-design/icons";
import {
  Card,
  Descriptions,
  Form,
  InputNumber,
  Modal,
  Select,
  Space,
  Typography,
  message,
  Popover,
  Button,
} from "antd";
import { useCallback, useEffect, useMemo, useState, useRef } from "react";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import Toolbar from "../../components/common/Toolbar";
import { meterService } from "../../services/meterService";
import { lookupService } from "../../services/lookupService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { formatMoney, pick, pickId, toArray } from "../../utils/data";

const { Text } = Typography;

function getPremiseId(record) {
  return pick(record, ["ma_mat_bang", "ma_mb", "MAMB"], undefined);
}

export default function MeterReadingPage() {
  const [open, setOpen] = useState(false);
  const [latestResult, setLatestResult] = useState(null);
  const [premises, setPremises] = useState([]);
  const [selectedPremise, setSelectedPremise] = useState(null);
  const [form] = Form.useForm();

  const [popoverOpen, setPopoverOpen] = useState(false);
  const [appliedFilters, setAppliedFilters] = useState({
    nam: undefined,
  });
  const [tempNam, setTempNam] = useState(undefined);
  const [keyword, setKeyword] = useState("");
  const timerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  const fetcher = useCallback((params) => meterService.list(params), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const applySearch = (val) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    timerRef.current = setTimeout(() => {
      setParams({
        ma_mat_bang: val || undefined,
        nam: appliedFilters.nam || undefined,
        page: 1,
        page_size: 20,
      });
    }, 500);
  };

  const handleApply = () => {
    const nextFilters = {
      nam: tempNam || undefined,
    };
    setAppliedFilters(nextFilters);

    setParams({
      ma_mat_bang: keyword || undefined,
      nam: nextFilters.nam,
      page: 1,
      page_size: 20,
    });
    setPopoverOpen(false);
  };

  const handleCancel = () => {
    setTempNam(appliedFilters.nam);
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempNam(undefined);
    setAppliedFilters({
      nam: undefined,
    });
    setParams({
      ma_mat_bang: keyword || undefined,
      page: 1,
      page_size: 20,
    });
    setPopoverOpen(false);
  };

  const handleReload = () => {
    setKeyword("");
    setAppliedFilters({
      nam: undefined,
    });
    setTempNam(undefined);
    setParams({
      page: 1,
      page_size: 20,
    });
    reload();
  };

  const loadPremises = useCallback(async () => {
    try {
      const data = await lookupService.meterPremises();
      setPremises(toArray(data));
    } catch (error) {
      showApiError(error);
    }
  }, []);

  useEffect(() => {
    loadPremises();
  }, [loadPremises]);

  const premiseOptions = useMemo(
    () =>
      premises
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
    [premises],
  );

  const handlePremiseChange = (value) => {
    const premise = premises.find((item) => getPremiseId(item) === value);
    setSelectedPremise(premise || null);
  };

  const openCreateModal = () => {
    form.resetFields();
    setSelectedPremise(null);
    setOpen(true);
    loadPremises();
  };

  const create = async () => {
    try {
      const values = await form.validateFields();
      const result = await meterService.create(values);

      message.success("Đã nhập chỉ số điện nước");
      setLatestResult(result);
      setOpen(false);
      form.resetFields();
      setSelectedPremise(null);
      reload();
      loadPremises();
    } catch (error) {
      showApiError(error);
    }
  };

  const columns = [
    {
      title: "Mã CSDN",
      render: (_, record) => pick(record, ["ma_chi_so_dien_nuoc", "ma_csdn", "MACSDN"]),
    },
    {
      title: "Mặt bằng",
      render: (_, record) => pick(record, ["ma_mat_bang", "ma_mb", "MAMB"]),
    },
    {
      title: "Kỳ",
      render: (_, record) => `${pick(record, ["thang", "THANG"])} / ${pick(record, ["nam", "NAM"])}`,
    },
    {
      title: "Điện đầu",
      render: (_, record) => pick(record, ["chi_so_dien_dau", "CHISODIENDAU"]),
    },
    {
      title: "Điện cuối",
      render: (_, record) => pick(record, ["chi_so_dien_cuoi", "CHISODIENCUOI"]),
    },
    {
      title: "Số điện",
      render: (_, record) => pick(record, ["so_dien_tieu_thu", "SODIEN_TIEUTHU"]),
    },
    {
      title: "Tiền điện",
      render: (_, record) => formatMoney(pick(record, ["tien_dien", "TIENDIEN"])),
    },
    {
      title: "Nước đầu",
      render: (_, record) => pick(record, ["chi_so_nuoc_dau", "CHISONUOCDAU"]),
    },
    {
      title: "Nước cuối",
      render: (_, record) => pick(record, ["chi_so_nuoc_cuoi", "CHISONUOCCUOI"]),
    },
    {
      title: "Số nước",
      render: (_, record) => pick(record, ["so_nuoc_tieu_thu", "SONUOC_TIEUTHU"]),
    },
    {
      title: "Tiền nước",
      render: (_, record) => formatMoney(pick(record, ["tien_nuoc", "TIENNUOC"])),
    },
  ];

  const activeFiltersCount = appliedFilters.nam ? 1 : 0;

  const filterContent = (
    <div style={{ padding: "8px", width: 250 }}>
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

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Button type="primary" danger onClick={handleCancel}>
          Hủy
        </Button>
        <Button type="primary" onClick={handleApply}>
          Áp dụng
        </Button>
      </div>
    </div>
  );

  return (
    <>
      <PageHeader
        title="Chỉ số điện nước"
        subtitle="Nhập và theo dõi chỉ số điện nước theo mặt bằng"
        actionText="Nhập chỉ số"
        actionIcon={<ThunderboltOutlined />}
        onAction={openCreateModal}
      />

      <Toolbar
        keyword={keyword}
        onKeywordChange={(val) => {
          setKeyword(val);
          applySearch(val);
        }}
        placeholder="Tìm kiếm mã Mặt bằng"
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
        rowKey={(record) => pickId(record, ["ma_chi_so_dien_nuoc", "ma_csdn", "MACSDN"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title="Nhập chỉ số điện nước"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={create}
        destroyOnClose
        okText="Lưu"
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
              placeholder="Chọn mặt bằng đang thuê"
              options={premiseOptions}
              optionFilterProp="label"
              onChange={handlePremiseChange}
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

          <Form.Item name="thang" label="Tháng" rules={[{ required: true, message: "Vui lòng nhập tháng" }]}>
            <InputNumber min={1} max={12} style={{ width: "100%" }} placeholder="Nhập tháng" />
          </Form.Item>

          <Form.Item name="nam" label="Năm" rules={[{ required: true, message: "Vui lòng nhập năm" }]}>
            <InputNumber min={2000} style={{ width: "100%" }} placeholder="Nhập năm" />
          </Form.Item>

          <Form.Item
            name="chi_so_dien_dau"
            label="Chỉ số điện đầu"
            rules={[{ required: true, message: "Vui lòng nhập chỉ số điện đầu" }]}
          >
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>

          <Form.Item
            name="chi_so_dien_cuoi"
            label="Chỉ số điện cuối"
            rules={[{ required: true, message: "Vui lòng nhập chỉ số điện cuối" }]}
          >
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>

          <Form.Item
            name="chi_so_nuoc_dau"
            label="Chỉ số nước đầu"
            rules={[{ required: true, message: "Vui lòng nhập chỉ số nước đầu" }]}
          >
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>

          <Form.Item
            name="chi_so_nuoc_cuoi"
            label="Chỉ số nước cuối"
            rules={[{ required: true, message: "Vui lòng nhập chỉ số nước cuối" }]}
          >
            <InputNumber min={0} style={{ width: "100%" }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
