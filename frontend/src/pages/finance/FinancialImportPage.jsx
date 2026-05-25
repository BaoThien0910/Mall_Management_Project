import { UploadOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Space, Upload, message } from "antd";
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

  const fetcher = useCallback((params) => financialImportService.list(params), []);
  const { items, loading, reload } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

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
        </Space>
      </Card>

      <ResponsiveTable
        rowKey={(record) => pickId(record, ["ma_import", "MAIMPORT"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />
    </>
  );
}
