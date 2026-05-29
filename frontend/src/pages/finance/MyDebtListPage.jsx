import { Button } from "antd";
import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import StatCard from "../../components/common/StatCard";
import { ROUTES } from "../../constants/routes";
import { debtService } from "../../services/debtService";
import { useCrudList } from "../../hooks/useCrudList";
import { pick, pickId, formatMoney } from "../../utils/data";

export default function MyDebtListPage() {
  const navigate = useNavigate();
  const fetcher = useCallback((p) => debtService.myDebts(p), []);
  const { items, loading } = useCrudList(fetcher, { page: 1, page_size: 20 });

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
      <ResponsiveTable
        rowKey={(r) => pickId(r, ["ma_cong_no", "ma_cn", "MACN"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />
    </>
  );
}