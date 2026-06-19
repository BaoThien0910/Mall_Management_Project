import { DownloadOutlined, EyeOutlined, PlusOutlined, FilterOutlined } from "@ant-design/icons";
import {
  Button,
  Descriptions,
  Form,
  InputNumber,
  Modal,
  Space,
  Table,
  message,
  Popover,
} from "antd";
import { useCallback, useState, useEffect } from "react";
import Toolbar from "../../components/common/Toolbar";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { useCrudList } from "../../hooks/useCrudList";
import { showApiError } from "../../services/apiClient";
import { financialReportService } from "../../services/financialReportService";
import { formatDate, formatMoney, pick, pickId } from "../../utils/data";

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

function getReportId(record) {
  return pickId(record, ["ma_bao_cao", "ma_bc", "MABC"]);
}

export default function FinancialReportPage() {
  const { role } = useAuth();
  const canCreate = role === ROLE.TP_KDTC;

  const [createOpen, setCreateOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [form] = Form.useForm();

  const [popoverOpen, setPopoverOpen] = useState(false);
  const [appliedFilters, setAppliedFilters] = useState({
    nam: undefined,
  });
  const [tempNam, setTempNam] = useState(undefined);

  const fetcher = useCallback((params) => financialReportService.list(params), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const handleApply = () => {
    const nextFilters = {
      nam: tempNam || undefined,
    };
    setAppliedFilters(nextFilters);

    setParams({
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
      page: 1,
      page_size: 20,
    });
    setPopoverOpen(false);
  };

  const handleReload = () => {
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

  const create = async () => {
    try {
      const values = await form.validateFields();
      await financialReportService.create(values);
      message.success("Đã lập báo cáo tài chính");
      setCreateOpen(false);
      form.resetFields();
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const openDetail = async (record) => {
    const maBc = getReportId(record);
    setDetailLoading(true);
    setDetailOpen(true);

    try {
      const data = await financialReportService.detail(maBc);
      setDetail(data);
    } catch (error) {
      showApiError(error);
      setDetailOpen(false);
    } finally {
      setDetailLoading(false);
    }
  };

  const exportExcel = async () => {
    const maBc = pick(detail?.bao_cao, ["ma_bao_cao", "MABC"], "bao-cao-tai-chinh");

    try {
      const blob = await financialReportService.exportExcel(maBc);
      downloadBlob(blob, `${maBc}.xlsx`);
    } catch (error) {
      showApiError(error);
    }
  };

  const listColumns = [
    {
      title: "MABC",
      render: (_, record) => getReportId(record),
    },
    {
      title: "MANV",
      render: (_, record) => pick(record, ["ma_nhan_vien_lap", "MANV"]),
    },
    {
      title: "KỲ CHỐT",
      render: (_, record) => pick(record, ["ky_chot", "KYCHOT"]),
      sorter: (a, b) => {
        const kyA = pick(a, ["ky_chot", "KYCHOT"]) || "";
        const kyB = pick(b, ["ky_chot", "KYCHOT"]) || "";
        const [mA, yA] = kyA.split("/").map(Number);
        const [mB, yB] = kyB.split("/").map(Number);
        if (yA !== yB) return yA - yB;
        return mA - mB;
      }
    },
    {
      title: "THAO TÁC",
      align: "right",
      render: (_, record) => (
        <Button size="small" icon={<EyeOutlined />} onClick={() => openDetail(record)}>
          Xem nội dung
        </Button>
      ),
    },
  ];

  const detailColumns = [
    {
      title: "MAHD",
      render: (_, record) => pick(record, ["ma_hop_dong", "MAHD"]),
    },
    {
      title: "MAKH",
      render: (_, record) => pick(record, ["ma_khach_thue", "MAKH"]),
    },
    {
      title: "MAMB",
      render: (_, record) => pick(record, ["ma_mat_bang", "MAMB"]),
    },
    {
      title: "KY",
      render: (_, record) => pick(record, ["ky", "KY"]),
    },
    {
      title: "TIEN THUE",
      align: "right",
      render: (_, record) => formatMoney(pick(record, ["tien_thue", "TIENTHUE"], 0)),
    },
    {
      title: "TIEN DIEN",
      align: "right",
      render: (_, record) => formatMoney(pick(record, ["tien_dien", "TIENDIEN"], 0)),
    },
    {
      title: "TIEN NUOC",
      align: "right",
      render: (_, record) => formatMoney(pick(record, ["tien_nuoc", "TIENNUOC"], 0)),
    },
    {
      title: "TIEN HOAN TRA",
      align: "right",
      render: (_, record) => formatMoney(pick(record, ["tien_hoan_tra", "TIENHOANTRA"], 0)),
    },
    {
      title: "CHI PHI BAO TRI",
      align: "right",
      render: (_, record) => formatMoney(pick(record, ["chi_phi_bao_tri", "CHIPHI_BAOTRI"], 0)),
    },
    {
      title: "TONG TIEN",
      align: "right",
      render: (_, record) => formatMoney(pick(record, ["tong_tien", "TONGTIEN"], 0)),
    },
    {
      title: "DA THANH TOAN",
      align: "right",
      render: (_, record) => formatMoney(pick(record, ["da_thanh_toan", "DA_THANH_TOAN"], 0)),
    },
    {
      title: "NO",
      align: "right",
      render: (_, record) => formatMoney(pick(record, ["no", "NO"], 0)),
    },
  ];

  const report = detail?.bao_cao;
  const summary = detail?.thong_ke || {};

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
        title="Báo cáo tài chính"
        subtitle="Danh sách báo cáo tài chính theo kỳ chốt"
        actionText={canCreate ? "Lập báo cáo" : undefined}
        actionIcon={<PlusOutlined />}
        onAction={canCreate ? () => setCreateOpen(true) : undefined}
      />

      <Toolbar
        onReload={handleReload}
        reloadAfterChildren
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
        rowKey={(record) => getReportId(record)}
        columns={listColumns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title="Lập báo cáo tài chính"
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        onOk={create}
        okText="Lập báo cáo"
        cancelText="Hủy"
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="thang"
            label="Tháng"
            rules={[{ required: true, message: "Vui lòng nhập tháng" }]}
          >
            <InputNumber min={1} max={12} style={{ width: "100%" }} placeholder="MM" />
          </Form.Item>

          <Form.Item
            name="nam"
            label="Năm"
            rules={[{ required: true, message: "Vui lòng nhập năm" }]}
          >
            <InputNumber min={2000} max={2100} style={{ width: "100%" }} placeholder="YYYY" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Nội dung báo cáo tài chính"
        open={detailOpen}
        onCancel={() => setDetailOpen(false)}
        width={1300}
        footer={[
          <Button key="close" onClick={() => setDetailOpen(false)}>
            Đóng
          </Button>,
          <Button key="excel" type="primary" icon={<DownloadOutlined />} onClick={exportExcel}>
            Tải Excel
          </Button>,
        ]}
      >
        <Space direction="vertical" size={16} style={{ width: "100%" }}>
          <Descriptions bordered size="small" column={3}>
            <Descriptions.Item label="MABC">
              {pick(report, ["ma_bao_cao", "MABC"])}
            </Descriptions.Item>
            <Descriptions.Item label="MANV">
              {pick(report, ["ma_nhan_vien_lap", "MANV"])}
            </Descriptions.Item>
            <Descriptions.Item label="KỲ CHỐT">
              {pick(report, ["ky_chot", "KYCHOT"])}
            </Descriptions.Item>
            <Descriptions.Item label="Ngày lập">
              {formatDate(pick(report, ["ngay_lap", "NGAYLAP"]))}
            </Descriptions.Item>
          </Descriptions>

          <Table
            rowKey={(record) => `${pick(record, ["ma_hop_dong", "MAHD"])}-${pick(record, ["stt", "STT"])}`}
            columns={detailColumns}
            dataSource={detail?.chi_tiet || []}
            loading={detailLoading}
            pagination={false}
            scroll={{ x: 1300 }}
            size="small"
          />

          <Descriptions bordered size="small" title="THONG KE" column={5}>
            <Descriptions.Item label="TONG SO HD">
              {pick(summary, ["tong_so_hd"], 0)}
            </Descriptions.Item>
            <Descriptions.Item label="TONG SO HD CON NO">
              {pick(summary, ["tong_so_hd_con_no"], 0)}
            </Descriptions.Item>
            <Descriptions.Item label="TONG">
              {formatMoney(pick(summary, ["tong"], 0))}
            </Descriptions.Item>
            <Descriptions.Item label="TONG TT">
              {formatMoney(pick(summary, ["tong_tt"], 0))}
            </Descriptions.Item>
            <Descriptions.Item label="TONG NO">
              {formatMoney(pick(summary, ["tong_no"], 0))}
            </Descriptions.Item>
          </Descriptions>
        </Space>
      </Modal>
    </>
  );
}
