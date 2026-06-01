import { DeleteOutlined, UploadOutlined, FilterOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Modal, Space, Upload, message, Popover, Select, InputNumber, Input } from "antd";
import { useCallback, useState, useRef, useEffect } from "react";
import Toolbar from "../../components/common/Toolbar";

const IMPORT_STATUS = ["Hợp lệ", "Lỗi", "Đã dùng tính công nợ"];
const LOAI_KHOAN_OPTIONS = ["Tiền thuê", "Phí bảo trì", "Hoàn trả"];

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { financialImportService } from "../../services/financialImportService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { formatMoney, pick, pickId } from "../../utils/data";

export default function FinancialImportPage() {
  const [file, setFile] = useState(null);
  const [isDeleteMode, setIsDeleteMode] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const [keyword, setKeyword] = useState("");
  const [popoverOpen, setPopoverOpen] = useState(false);
  const timerRef = useRef(null);

  const [appliedFilters, setAppliedFilters] = useState({
    nam: undefined,
    loai_khoan: undefined,
    trang_thai: undefined,
  });

  const [tempNam, setTempNam] = useState(undefined);
  const [tempLoaiKhoan, setTempLoaiKhoan] = useState(undefined);
  const [tempTrangThai, setTempTrangThai] = useState(undefined);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  const fetcher = useCallback((params) => financialImportService.list(params), []);
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
      nam: tempNam || undefined,
      loai_khoan: tempLoaiKhoan || undefined,
      trang_thai: tempTrangThai || undefined,
    };
    setAppliedFilters(nextFilters);

    const cleanFilters = {};
    Object.keys(nextFilters).forEach((key) => {
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
    setTempNam(appliedFilters.nam);
    setTempLoaiKhoan(appliedFilters.loai_khoan);
    setTempTrangThai(appliedFilters.trang_thai);
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempNam(undefined);
    setTempLoaiKhoan(undefined);
    setTempTrangThai(undefined);

    setAppliedFilters({
      nam: undefined,
      loai_khoan: undefined,
      trang_thai: undefined,
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
      nam: undefined,
      loai_khoan: undefined,
      trang_thai: undefined,
    });
    setTempNam(undefined);
    setTempLoaiKhoan(undefined);
    setTempTrangThai(undefined);
    setParams({
      page: 1,
      page_size: 20,
    });
    reload();
  };

  const activeFiltersCount =
    (appliedFilters.nam ? 1 : 0) +
    (appliedFilters.loai_khoan ? 1 : 0) +
    (appliedFilters.trang_thai ? 1 : 0);

  const filterContent = (
    <div style={{ padding: "8px", width: 300 }}>
      <div style={{ marginBottom: "12px" }}>
        <div style={{ fontWeight: 600, marginBottom: "6px" }}>Năm</div>
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

      <div style={{ marginBottom: "12px" }}>
        <div style={{ fontWeight: 600, marginBottom: "6px" }}>Loại khoản</div>
        <Select
          placeholder="Chọn loại khoản"
          value={tempLoaiKhoan}
          onChange={setTempLoaiKhoan}
          style={{ width: "100%" }}
          allowClear
          options={LOAI_KHOAN_OPTIONS.map((item) => ({ value: item, label: item }))}
        />
      </div>

      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, marginBottom: "6px" }}>Trạng thái</div>
        <Select
          placeholder="Chọn trạng thái"
          value={tempTrangThai}
          onChange={setTempTrangThai}
          style={{ width: "100%" }}
          allowClear
          options={IMPORT_STATUS.map((item) => ({ value: item, label: item }))}
        />
      </div>

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

  const cancelDeleteMode = () => {
    setIsDeleteMode(false);
    setSelectedRowKeys([]);
  };

  const handleBatchDelete = () => {
    if (selectedRowKeys.length === 0) return;

    Modal.confirm({
      title: "Xác nhận xóa",
      content: `Bạn có chắc chắn muốn xóa ${selectedRowKeys.length} dòng dữ liệu import tài chính đã chọn không? Bản ghi đã dùng để tính công nợ sẽ không thể xóa. Hành động này không thể hoàn tác.`,
      okText: "Xóa",
      okType: "danger",
      cancelText: "Hủy",
      onOk: async () => {
        setDeleteLoading(true);
        try {
          await financialImportService.deleteMany(selectedRowKeys);
          message.success("Xóa dữ liệu import tài chính thành công!");
          setSelectedRowKeys([]);
          setIsDeleteMode(false);
          reload();
        } catch (error) {
          showApiError(error);
        } finally {
          setDeleteLoading(false);
        }
      },
    });
  };

  const upload = async () => {
    if (!file) return message.warning("Chọn file .xlsx trước");

    try {
      const result = await financialImportService.upload(file);
      message.success(`Import thành công: ${result?.so_dong_hop_le ?? ""} dòng hợp lệ`);
      setFile(null);
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const columns = [
    {
      title: "Mã import",
      render: (_, record) => pick(record, ["ma_import", "MAIMPORT"]),
    },
    {
      title: "Hợp đồng",
      render: (_, record) => pick(record, ["ma_hop_dong", "MAHD"]),
    },
    {
      title: "Kỳ",
      render: (_, record) => `${pick(record, ["thang", "THANG"])} / ${pick(record, ["nam", "NAM"])}`,
    },
    {
      title: "Loại khoản",
      render: (_, record) => pick(record, ["loai_khoan", "LOAIKHOAN"]),
    },
    {
      title: "Số tiền",
      render: (_, record) => formatMoney(pick(record, ["so_tien", "SOTIEN"])),
    },
    {
      title: "Trạng thái",
      render: (_, record) => <StatusTag value={pick(record, ["trang_thai", "TRANGTHAI"])} />,
    },
    {
      title: "Lỗi",
      render: (_, record) => pick(record, ["loi_chi_tiet", "LOI_CHITIET"], "-"),
    },
  ];

  return (
    <>
      <PageHeader title="Import tài chính" breadcrumb={["Tài chính", "Import Excel"]} />

      <Card className="toolbar-card">
        <Alert
          type="info"
          showIcon
          className="mb-16"
          message="Mẫu Excel tài chính"
          description="Header: MAHD | THANG | NAM | LOAIKHOAN | SOTIEN | GHICHU. LOAIKHOAN hợp lệ: Tiền thuê, Phí bảo trì, Hoàn trả. Tiền điện/nước được lấy từ chức năng Chỉ số điện nước, không nhập trong Excel."
        />

        <Space wrap className="toolbar-space">
          {!isDeleteMode ? (
            <>
              <Upload
                beforeUpload={(selectedFile) => {
                  setFile(selectedFile);
                  return false;
                }}
                maxCount={1}
                accept=".xlsx,.xls"
              >
                <Button icon={<UploadOutlined />}>Chọn file .xlsx</Button>
              </Upload>
              <Button type="primary" onClick={upload} disabled={!file}>
                Tải lên và xử lý
              </Button>
              <Button
                type="primary"
                danger
                icon={<DeleteOutlined />}
                onClick={() => setIsDeleteMode(true)}
              >
                Xóa
              </Button>
            </>
          ) : (
            <>
              <Button
                type="primary"
                danger
                icon={<DeleteOutlined />}
                loading={deleteLoading}
                disabled={selectedRowKeys.length === 0}
                onClick={handleBatchDelete}
              >
                Xác nhận xóa ({selectedRowKeys.length} dòng)
              </Button>
              <Button onClick={cancelDeleteMode}>
                Hủy
              </Button>
            </>
          )}
        </Space>
      </Card>

      <Toolbar
        keyword={keyword}
        onKeywordChange={(val) => {
          setKeyword(val);
          applySearch(val);
        }}
        placeholder="Tìm kiếm mã Hợp đồng"
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
        rowKey={(record) => pickId(record, ["ma_import", "MAIMPORT"])}
        columns={columns}
        dataSource={items}
        loading={loading}
        rowSelection={isDeleteMode ? {
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys),
        } : undefined}
      />
    </>
  );
}
