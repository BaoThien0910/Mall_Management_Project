import { Button, Popover, Select, Space, InputNumber } from "antd";
import { FilterOutlined } from "@ant-design/icons";
import { useCallback, useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import StatCard from "../../components/common/StatCard";
import Toolbar from "../../components/common/Toolbar";
import { ROUTES } from "../../constants/routes";
import { CONG_NO_STATUS } from "../../constants/statuses";
import { debtService } from "../../services/debtService";
import { useCrudList } from "../../hooks/useCrudList";
import { pick, pickId, formatMoney } from "../../utils/data";

export default function MyDebtListPage() {
  const navigate = useNavigate();
  const [keyword, setKeyword] = useState("");
  const [popoverOpen, setPopoverOpen] = useState(false);

  const [appliedFilters, setAppliedFilters] = useState({
    nam: undefined,
    trang_thai: undefined,
  });

  const [tempNam, setTempNam] = useState(undefined);
  const [tempTrangThai, setTempTrangThai] = useState(undefined);

  const timerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  const fetcher = useCallback((p) => debtService.myDebts(p), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, { page: 1, page_size: 20 });

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
    setTempTrangThai(appliedFilters.trang_thai);
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempNam(undefined);
    setTempTrangThai(undefined);

    setAppliedFilters({
      nam: undefined,
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
      trang_thai: undefined,
    });
    setTempNam(undefined);
    setTempTrangThai(undefined);
    setParams({
      page: 1,
      page_size: 20,
    });
    reload();
  };

  const activeFiltersCount =
    (appliedFilters.nam ? 1 : 0) +
    (appliedFilters.trang_thai ? 1 : 0);

  const filterContent = (
    <div style={{ padding: "8px", width: 300 }}>
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

      <div style={{ marginBottom: "20px" }}>
        <div style={{ fontWeight: 600, marginBottom: "8px" }}>Trạng thái</div>
        <Select
          placeholder="Chọn trạng thái"
          value={tempTrangThai}
          onChange={setTempTrangThai}
          style={{ width: "100%" }}
          allowClear
          options={CONG_NO_STATUS.map((item) => ({ value: item, label: item }))}
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

  const unpaid = items.filter((r) => pick(r, ["trang_thai", "TRANGTHAI"]) !== "Đã thanh toán");
  const total = unpaid.reduce((s, r) => s + Number(pick(r, ["tong_tien", "TONGTIEN"], 0)), 0);

  const columns = [
    {
      title: "Mã CN",
      render: (_, record) => pick(record, ["ma_cong_no", "ma_cn", "MACN"]),
    },
    {
      title: "Hợp đồng",
      render: (_, record) => pick(record, ["ma_hop_dong", "ma_hd", "MAHD"]),
    },
    {
      title: "Kỳ",
      render: (_, record) => `${pick(record, ["thang", "THANG"])} / ${pick(record, ["nam", "NAM"])}`,
    },
    {
      title: "Tiền thuê",
      render: (_, record) => formatMoney(pick(record, ["tien_thue", "TIENTHUE"])),
    },
    {
      title: "Tiền điện",
      render: (_, record) => formatMoney(pick(record, ["tien_dien", "TIENDIEN"])),
    },
    {
      title: "Tiền nước",
      render: (_, record) => formatMoney(pick(record, ["tien_nuoc", "TIENNUOC"])),
    },
    {
      title: "Phí bảo trì",
      render: (_, record) => formatMoney(pick(record, ["phi_bao_tri", "PHIBAOTRI"])),
    },
    {
      title: "Hoàn trả",
      render: (_, record) => formatMoney(pick(record, ["tien_hoan", "TIENHOAN"])),
    },
    {
      title: "Tổng tiền",
      render: (_, record) => formatMoney(pick(record, ["tong_tien", "TONGTIEN"])),
    },
    {
      title: "Hạn thanh toán",
      render: (_, record) => pick(record, ["han_thanh_toan", "HAN_THANHTOAN"], "-"),
    },
    {
      title: "Trạng thái",
      render: (_, record) => <StatusTag value={pick(record, ["trang_thai", "TRANGTHAI"])} />,
    },
    {
      title: "Thao tác",
      align: "right",
      render: (_, r) =>
        pick(r, ["trang_thai", "TRANGTHAI"]) !== "Đã thanh toán" ? (
          <Button
            type="link"
            onClick={() =>
              navigate(
                `${ROUTES.PAYMENT}?ma_cong_no=${pickId(r, ["ma_cong_no", "ma_cn", "MACN"])}`
              )
            }
          >
            Thanh toán
          </Button>
        ) : null, 
    },
  ];

  return (
    <>
      <PageHeader
        title="Công nợ & Thanh toán"
        breadcrumb={["Trang chủ", "Công nợ & thanh toán"]}
      />
      <div className="stats-grid">
        <StatCard label="Số kỳ công nợ" value={items.length} />
        <StatCard label="Tổng còn phải trả" value={formatMoney(total)} danger />
        <StatCard
          label="Kỳ quá hạn"
          value={items.filter((r) => pick(r, ["trang_thai", "TRANGTHAI"]) === "Quá hạn").length}
        />
      </div>

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
        rowKey={(r) => pickId(r, ["ma_cong_no", "ma_cn", "MACN"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />
    </>
  );
}