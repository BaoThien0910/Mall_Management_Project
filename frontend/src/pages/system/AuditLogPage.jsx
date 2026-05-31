import { useCallback, useState } from "react";
import { DatePicker, Select } from "antd";
import dayjs from "dayjs";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import Toolbar from "../../components/common/Toolbar";
import { auditService } from "../../services/auditService";
import { pick, pickId } from "../../utils/data";
import { useCrudList } from "../../hooks/useCrudList";

const HANH_DONG_OPTIONS = [
  "Đăng nhập",
  "Đăng xuất",
  "Tạo mới",
  "Cập nhật",
  "Xóa",
  "Duyệt",
  "Vượt quyền",
];

export default function AuditLogPage() {
  const [tuNgay, setTuNgay] = useState("");
  const [denNgay, setDenNgay] = useState("");
  const [rangePreset, setRangePreset] = useState(null);
  const [hanhDong, setHanhDong] = useState(undefined);

  const fetcher = useCallback((p) => auditService.list(p), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const handleSearch = () => {
    setParams({
      hanh_dong: hanhDong || undefined,
      tu_ngay: tuNgay ? `${tuNgay}T00:00:00` : undefined,
      den_ngay: denNgay ? `${denNgay}T23:59:59` : undefined,
      page: 1,
      page_size: 20,
    });
  };

  const handleReload = () => {
    setTuNgay("");
    setDenNgay("");
    setRangePreset(null);
    setHanhDong(undefined);
    setParams({
      hanh_dong: undefined,
      tu_ngay: undefined,
      den_ngay: undefined,
      page: 1,
      page_size: 20,
    });
  };

  const handlePresetChange = (value) => {
    setRangePreset(value);
    const today = dayjs().format("YYYY-MM-DD");
    if (value === "today") {
      setTuNgay(today);
      setDenNgay(today);
    } else if (value === "yesterday") {
      const yesterday = dayjs().subtract(1, "day").format("YYYY-MM-DD");
      setTuNgay(yesterday);
      setDenNgay(yesterday);
    } else if (value === "7days") {
      const sevenDaysAgo = dayjs().subtract(6, "day").format("YYYY-MM-DD");
      setTuNgay(sevenDaysAgo);
      setDenNgay(today);
    } else if (value === "30days") {
      const thirtyDaysAgo = dayjs().subtract(29, "day").format("YYYY-MM-DD");
      setTuNgay(thirtyDaysAgo);
      setDenNgay(today);
    }
  };

  const columns = [
    {
      title: "Thời gian",
      render: (_, r) => {
        const val = pick(r, ["thoi_gian", "THOIGIAN"]);
        if (!val) return "-";
        const d = dayjs(val);
        return d.isValid() ? d.format("DD/MM/YYYY HH:mm:ss") : val;
      },
    },
    {
      title: "Tài khoản",
      render: (_, r) => pick(r, ["ma_tai_khoan", "ma_tk", "MATK"]),
    },
    {
      title: "Hành động",
      render: (_, r) => pick(r, ["hanh_dong", "HANHDONG"]),
    },
    {
      title: "Đối tượng",
      render: (_, r) => pick(r, ["doi_tuong", "DOITUONG"]),
    },
    {
      title: "Chi tiết",
      render: (_, r) => pick(r, ["chi_tiet", "CHITIET"]),
    },
  ];

  return (
    <>
      <PageHeader title="Nhật ký thao tác" breadcrumb={["Quản trị", "Nhật ký"]} />
      <Toolbar
        onSearch={handleSearch}
        onReload={handleReload}
        reloadAfterChildren
      >
        <span style={{ display: "inline-flex", alignItems: "center", gap: "8px" }}>
          <span>From:</span>
          <DatePicker
            value={tuNgay ? dayjs(tuNgay) : null}
            onChange={(date) => {
              setTuNgay(date ? dayjs(date).format("YYYY-MM-DD") : "");
              setRangePreset(null);
            }}
            format="DD/MM/YYYY"
            placeholder="Từ ngày"
            style={{ width: 130 }}
            allowClear={false}
          />
          <span>- To:</span>
          <DatePicker
            value={denNgay ? dayjs(denNgay) : null}
            onChange={(date) => {
              setDenNgay(date ? dayjs(date).format("YYYY-MM-DD") : "");
              setRangePreset(null);
            }}
            format="DD/MM/YYYY"
            placeholder="Đến ngày"
            style={{ width: 130 }}
            allowClear={false}
          />
        </span>
        <Select
          placeholder="Chọn nhanh"
          value={rangePreset || undefined}
          onChange={handlePresetChange}
          style={{ width: 130 }}
          allowClear
          onClear={() => {
            setTuNgay("");
            setDenNgay("");
            setRangePreset(null);
          }}
          options={[
            { value: "today", label: "Hôm nay" },
            { value: "yesterday", label: "Hôm qua" },
            { value: "7days", label: "7 ngày qua" },
            { value: "30days", label: "30 ngày qua" },
          ]}
        />
        <Select
          placeholder="Hành động"
          value={hanhDong || undefined}
          onChange={setHanhDong}
          style={{ width: 130 }}
          allowClear
          options={HANH_DONG_OPTIONS.map((action) => ({ value: action, label: action }))}
        />
      </Toolbar>
      <ResponsiveTable
        rowKey={(r) => pickId(r, ["ma_nhat_ky", "MANHATKY"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />
    </>
  );
}
