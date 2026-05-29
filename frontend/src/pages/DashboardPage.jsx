import { useEffect, useState } from "react";
import { Card, Col, Row, Table, Tag, Typography, Spin, message } from "antd";
import { Link } from "react-router-dom";
import PageHeader from "../components/common/PageHeader";
import StatCard from "../components/common/StatCard";
import { ROLE, ROLE_LABEL } from "../constants/roles";
import { ROUTES } from "../constants/routes";
import { useAuth } from "../hooks/useAuth";
import { dashboardService } from "../services/dashboardService";

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
  
  const [dashboardData, setDashboardData] = useState({
    summary_cards: [],
    menu_badges: {}
  });
  const [loading, setLoading] = useState(true);

  const actions = actorActions[role] || [];
  const isTenant = role === ROLE.KHACH_THUE;

  // Gọi API thông qua axios
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const response = await dashboardService.getMyDashboard();
        const data = response.summary_cards ? response : (response.data?.data || response.data);
        
        console.log("DEBUG API DASHBOARD:", data); //debug

        if (data) {
          setDashboardData(data);
        }
      } catch (error) {
        console.error("Lỗi khi tải dữ liệu dashboard:", error);
        message.error("Không thể tải dữ liệu thống kê.");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const columns = [
    { title: isTenant ? "Mục cần xử lý" : "Nghiệp vụ", dataIndex: "name" },
    { title: "Trạng thái", dataIndex: "status", render: (v) => <Tag color="processing">{v}</Tag> },
    { title: "Thao tác", dataIndex: "to", render: (to) => <Link to={to}>Truy cập</Link> },
  ];
  
  const rows = actions.map(([name, to], idx) => ({ id: idx, name, to, status: "Sẵn sàng" }));

  const checkDangerCard = (key) => {
    const dangerKeys = ['disabled_accounts', 'pending_incidents', 'import_errors', 'unpaid_debts', 'open_incidents'];
    return dangerKeys.includes(key);
  };

  return (
    <>
      <PageHeader
        title={isTenant ? "Cổng khách thuê" : `Chào buổi sáng, ${ROLE_LABEL[role] || "Người dùng"}`}
        subtitle={isTenant ? "Theo dõi hợp đồng, công nợ và yêu cầu hỗ trợ của bạn." : "Tình hình hoạt động trung tâm hôm nay."}
        breadcrumb={[isTenant ? "Trang chủ" : "Quản trị"]}
      />
      <Spin spinning={loading}>
        <Row gutter={[16, 16]}>
          {dashboardData.summary_cards.map((card, index) => (
            <Col xs={24} md={12} xl={6} key={card.key || index}>
              <StatCard 
                label={card.title} 
                value={
                  card.key.includes('revenue') || card.key === 'total_payable' 
                    ? `${Number(card.value).toLocaleString('vi-VN')} đ` 
                    : card.value
                } 
                hint={card.description || card.status || "Cập nhật hôm nay"} 
                danger={checkDangerCard(card.key)}
              />
            </Col>
          ))}

          {!loading && dashboardData.summary_cards.length === 0 && (
             <Col span={24}>
                <Text type="secondary">Chưa có dữ liệu thống kê cho vai trò của bạn.</Text>
             </Col>
          )}
        </Row>
      </Spin>

      <Card className="section-card" style={{ marginTop: 24 }} title={isTenant ? "Chức năng của khách thuê" : "Chức năng theo vai trò"}>
        <Table columns={columns} dataSource={rows} rowKey="id" pagination={false} scroll={{ x: 720 }} />
      </Card>
    </>
  );
}