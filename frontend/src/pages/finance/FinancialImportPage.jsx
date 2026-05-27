import { DeleteOutlined, UploadOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Modal, Space, Upload, message } from "antd";
import { useCallback, useState } from "react";

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

  const fetcher = useCallback((params) => financialImportService.list(params), []);
  const { items, loading, reload } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

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
