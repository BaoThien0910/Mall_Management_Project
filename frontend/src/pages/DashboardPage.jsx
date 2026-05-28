import { Button, Card, Col, Row, Space, Table, Tag, Typography } from "antd";
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import StatCard from "../components/common/StatCard";
import { ROLE, ROLE_LABEL } from "../constants/roles";
import { ROUTES } from "../constants/routes";
import { useAuth } from "../hooks/useAuth";

const { Text } = Typography;

const actorActions = {
  [ROLE.QTV]: [
    ["Quản lý tài khoản", ROUTES.ACCOUNTS], ["Vai trò & quyền", ROUTES.RBAC], ["Nhật ký thao tác", ROUTES.AUDIT]
  ],
  [ROLE.BQL]: [
    ["Duyệt yêu cầu thuê thêm", ROUTES.RENT_REQUESTS], ["Duyệt sự cố bảo trì", ROUTES.INCIDENTS], ["Ban hành thông báo", ROUTES.NOTIFICATIONS], ["Xem báo cáo tài chính", ROUTES.FINANCIAL_REPORTS]
  ],
  [ROLE.TP_KDTC]: [
    ["Số hóa hợp đồng", ROUTES.CONTRACTS], ["Import tài chính", ROUTES.FINANCIAL_IMPORT], ["Tính công nợ", ROUTES.DEBTS], ["Báo cáo tài chính", ROUTES.FINANCIAL_REPORTS]
  ],
  [ROLE.NV_KDTC]: [
    ["Số hóa hợp đồng", ROUTES.CONTRACTS], ["Import tài chính", ROUTES.FINANCIAL_IMPORT], ["Công nợ", ROUTES.DEBTS]
  ],
  [ROLE.TP_VHBT]: [
    ["Mặt bằng", ROUTES.PREMISES], ["Chỉ số điện nước", ROUTES.PREMISES], ["Phân công sự cố", ROUTES.INCIDENTS], ["Lịch bảo trì", ROUTES.MAINTENANCE_SCHEDULES], ["Báo cáo bảo trì", ROUTES.MAINTENANCE_REPORTS]
  ],
  [ROLE.NV_VHBT]: [
    ["Mặt bằng", ROUTES.PREMISES], ["Nhập chỉ số điện nước", ROUTES.PREMISES], ["Xử lý sự cố", ROUTES.INCIDENTS], ["Lịch bảo trì", ROUTES.MAINTENANCE_SCHEDULES]
  ],
  [ROLE.KHACH_THUE]: [
    ["Mặt bằng còn trống", ROUTES.PREMISES], ["Hợp đồng của tôi", ROUTES.MY_CONTRACTS], ["Yêu cầu thuê thêm", ROUTES.RENT_REQUESTS], ["Công nợ & thanh toán", ROUTES.MY_DEBTS], ["Yêu cầu sửa chữa", ROUTES.INCIDENTS]
  ],
};

export default function DashboardPage() {
  const { user, role } = useAuth();
  const actions = actorActions[role] || [];
  const isTenant = role === ROLE.KHACH_THUE;
  const columns = [
    { title: isTenant ? "Mục cần xử lý" : "Nghiệp vụ", dataIndex: "name" },
    { title: "Trạng thái", dataIndex: "status", render: (v) => <Tag color="processing">{v}</Tag> },
    { title: "Thao tác", dataIndex: "to", render: (to) => <Link to={to}>Truy cập</Link> },
  ];
  const rows = actions.map(([name, to], idx) => ({ id: idx, name, to, status: "Sẵn sàng" }));

  return (
    <>
      <PageHeader
        title={isTenant ? "Cổng khách thuê" : `Chào buổi sáng, ${ROLE_LABEL[role] || "Người dùng"}`}
        subtitle={isTenant ? "Theo dõi hợp đồng, công nợ và yêu cầu hỗ trợ của bạn." : "Tình hình hoạt động trung tâm hôm nay."}
        breadcrumb={[isTenant ? "Trang chủ" : "Quản trị"]}
      />
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12} xl={6}><StatCard label={isTenant ? "Số kỳ công nợ" : "Tổng doanh thu"} value={isTenant ? "2" : "12,4 tỷ đ"} hint={isTenant ? "Theo dữ liệu thanh toán" : "↑ +8,2% so với kỳ trước"} /></Col>
        <Col xs={24} md={12} xl={6}><StatCard label={isTenant ? "Tổng còn phải trả" : "Tỷ lệ lấp đầy"} value={isTenant ? "0 đ" : "94%"} hint="Ổn định" /></Col>
        <Col xs={24} md={12} xl={6}><StatCard label={isTenant ? "Kỳ quá hạn" : "Lượt khách"} value={isTenant ? "0" : "45.210"} hint="↑ +2,4% so với kỳ trước" /></Col>
        <Col xs={24} md={12} xl={6}><StatCard label="Yêu cầu bảo trì" value="12" hint="Đang chờ xử lý" danger /></Col>
      </Row>
      <Card className="section-card" title={isTenant ? "Chức năng của khách thuê" : "Chức năng theo vai trò"}>
        <Table columns={columns} dataSource={rows} rowKey="id" pagination={false} scroll={{ x: 720 }} />
      </Card>
    </>
  );
}
