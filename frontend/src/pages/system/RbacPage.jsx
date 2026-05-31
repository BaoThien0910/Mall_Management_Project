import {
  Card,
  Col,
  Empty,
  List,
  Row,
  Space,
  Tag,
  Typography,
} from "antd";
import { useMemo, useState } from "react";
import { CheckCircleOutlined } from "@ant-design/icons";

import PageHeader from "../../components/common/PageHeader";
import { ROLE, ROLE_LABEL } from "../../constants/roles";

const { Text, Paragraph } = Typography;

const ROLE_ORDER = [
  ROLE.QTV,
  ROLE.BQL,
  ROLE.TP_KDTC,
  ROLE.NV_KDTC,
  ROLE.TP_VHBT,
  ROLE.NV_VHBT,
  ROLE.KHACH_THUE,
];

const ROLE_PERMISSION_GROUPS = {
  [ROLE.QTV]: {
    roleName: "Quản trị viên",
    description:
      "Quản lý tài khoản, theo dõi vai trò - phân quyền và giám sát hệ thống.",
    groups: [
      {
        module: "Dashboard",
        permissions: ["Xem dashboard tổng quan hệ thống"],
      },
      {
        module: "Tài khoản",
        permissions: [
          "Xem danh sách tài khoản",
          "Tạo tài khoản cho nhân viên hoặc khách thuê",
          "Vô hiệu hóa tài khoản",
          "Khôi phục tài khoản",
        ],
      },
      {
        module: "Vai trò và phân quyền",
        permissions: [
          "Xem danh sách vai trò",
          "Xem danh sách quyền của từng vai trò",
        ],
      },
      {
        module: "Nhật ký hệ thống",
        permissions: ["Xem nhật ký thao tác trong hệ thống"],
      },
      {
        module: "Thông báo",
        permissions: ["Xem thông báo hệ thống"],
      },
    ],
  },

  [ROLE.BQL]: {
    roleName: "Ban Quản Lý",
    description:
      "Giám sát hoạt động tổng thể, duyệt yêu cầu và ban hành thông báo.",
    groups: [
      {
        module: "Dashboard",
        permissions: ["Xem dashboard dành cho Ban Quản Lý"],
      },
      {
        module: "Mặt bằng",
        permissions: ["Xem danh sách mặt bằng", "Xem tình trạng mặt bằng"],
      },
      {
        module: "Hợp đồng",
        permissions: ["Xem danh sách hợp đồng", "Xem chi tiết hợp đồng"],
      },
      {
        module: "Yêu cầu thuê thêm",
        permissions: [
          "Xem danh sách yêu cầu thuê thêm",
          "Duyệt yêu cầu thuê thêm",
          "Từ chối yêu cầu thuê thêm",
        ],
      },
      {
        module: "Sự cố bảo trì",
        permissions: [
          "Xem danh sách sự cố bảo trì",
          "Duyệt yêu cầu xử lý sự cố",
          "Từ chối yêu cầu xử lý sự cố",
        ],
      },
      {
        module: "Báo cáo",
        permissions: [
          "Xem báo cáo tài chính",
          "Xem báo cáo bảo trì",
          "Theo dõi tình hình vận hành trung tâm thương mại",
        ],
      },
      {
        module: "Thông báo",
        permissions: [
          "Xem thông báo",
          "Tạo thông báo",
          "Ban hành thông báo",
          "Thu hồi thông báo",
        ],
      },
      {
        module: "Nhật ký hệ thống",
        permissions: ["Xem nhật ký thao tác hệ thống"],
      },
    ],
  },

  [ROLE.TP_KDTC]: {
    roleName: "Trưởng phòng Kinh doanh - Tài chính",
    description:
      "Quản lý hợp đồng, dữ liệu tài chính, công nợ và báo cáo tài chính.",
    groups: [
      {
        module: "Dashboard",
        permissions: ["Xem dashboard kinh doanh - tài chính"],
      },
      {
        module: "Hợp đồng",
        permissions: [
          "Xem danh sách hợp đồng",
          "Xem chi tiết hợp đồng",
          "Tạo hợp đồng thuê mặt bằng",
          "Số hóa hợp đồng",
        ],
      },
      {
        module: "Import tài chính",
        permissions: [
          "Xem lịch sử import dữ liệu tài chính",
          "Import file Excel dữ liệu tài chính",
          "Xem các dòng dữ liệu import lỗi",
          "Xóa dòng dữ liệu import lỗi hoặc chưa dùng",
        ],
      },
      {
        module: "Công nợ",
        permissions: [
          "Xem danh sách công nợ",
          "Tính công nợ theo tháng",
          "Theo dõi trạng thái công nợ",
        ],
      },
      {
        module: "Thanh toán",
        permissions: [
          "Xem giao dịch thanh toán",
          "Theo dõi kết quả thanh toán công nợ",
        ],
      },
      {
        module: "Báo cáo tài chính",
        permissions: [
          "Xem danh sách báo cáo tài chính",
          "Xem chi tiết báo cáo tài chính",
          "Lập báo cáo công nợ",
          "Lập báo cáo doanh số",
          "Ban hành báo cáo tài chính",
        ],
      },
      {
        module: "Thông báo",
        permissions: ["Xem thông báo"],
      },
    ],
  },

  [ROLE.NV_KDTC]: {
    roleName: "Nhân viên Kinh doanh - Tài chính",
    description:
      "Thực hiện nghiệp vụ hợp đồng, import dữ liệu tài chính và tính công nợ.",
    groups: [
      {
        module: "Dashboard",
        permissions: ["Xem dashboard kinh doanh - tài chính"],
      },
      {
        module: "Hợp đồng",
        permissions: [
          "Xem danh sách hợp đồng",
          "Xem chi tiết hợp đồng",
          "Tạo hợp đồng thuê mặt bằng",
          "Số hóa hợp đồng",
        ],
      },
      {
        module: "Import tài chính",
        permissions: [
          "Xem lịch sử import dữ liệu tài chính",
          "Import file Excel dữ liệu tài chính",
          "Xem các dòng dữ liệu import lỗi",
          "Xóa dòng dữ liệu import lỗi hoặc chưa dùng",
        ],
      },
      {
        module: "Công nợ",
        permissions: [
          "Xem danh sách công nợ",
          "Tính công nợ theo tháng",
          "Theo dõi trạng thái công nợ",
        ],
      },
      {
        module: "Thanh toán",
        permissions: ["Xem giao dịch thanh toán"],
      },
      {
        module: "Thông báo",
        permissions: ["Xem thông báo"],
      },
    ],
  },

  [ROLE.TP_VHBT]: {
    roleName: "Trưởng phòng Vận hành - Bảo trì",
    description:
      "Quản lý mặt bằng, chỉ số điện nước, sự cố, lịch bảo trì và báo cáo bảo trì.",
    groups: [
      {
        module: "Dashboard",
        permissions: ["Xem dashboard vận hành - bảo trì"],
      },
      {
        module: "Mặt bằng",
        permissions: [
          "Xem danh sách mặt bằng",
          "Xem chi tiết mặt bằng",
          "Tạo mặt bằng",
          "Cập nhật thông tin mặt bằng",
          "Xóa mặt bằng",
        ],
      },
      {
        module: "Chỉ số điện nước",
        permissions: [
          "Xem danh sách chỉ số điện nước",
          "Nhập chỉ số điện nước theo mặt bằng",
        ],
      },
      {
        module: "Sự cố bảo trì",
        permissions: [
          "Xem danh sách sự cố bảo trì",
          "Phân công nhân viên xử lý sự cố",
          "Cập nhật kết quả xử lý sự cố",
          "Cập nhật chi phí xử lý sự cố",
        ],
      },
      {
        module: "Lịch bảo trì",
        permissions: [
          "Xem danh sách lịch bảo trì",
          "Lập lịch bảo trì mặt bằng",
        ],
      },
      {
        module: "Báo cáo bảo trì",
        permissions: [
          "Xem danh sách báo cáo bảo trì",
          "Xem chi tiết báo cáo bảo trì",
          "Lập báo cáo trạng thái mặt bằng",
        ],
      },
      {
        module: "Thông báo",
        permissions: ["Xem thông báo"],
      },
    ],
  },

  [ROLE.NV_VHBT]: {
    roleName: "Nhân viên Vận hành - Bảo trì",
    description:
      "Thực hiện nghiệp vụ vận hành, nhập chỉ số điện nước và xử lý bảo trì.",
    groups: [
      {
        module: "Dashboard",
        permissions: ["Xem dashboard vận hành - bảo trì"],
      },
      {
        module: "Mặt bằng",
        permissions: [
          "Xem danh sách mặt bằng",
          "Xem chi tiết mặt bằng",
          "Tạo mặt bằng",
          "Cập nhật thông tin mặt bằng",
          "Xóa mặt bằng",
        ],
      },
      {
        module: "Chỉ số điện nước",
        permissions: [
          "Xem danh sách chỉ số điện nước",
          "Nhập chỉ số điện nước theo mặt bằng",
        ],
      },
      {
        module: "Sự cố bảo trì",
        permissions: [
          "Xem danh sách sự cố bảo trì",
          "Cập nhật kết quả xử lý sự cố",
          "Cập nhật chi phí xử lý sự cố",
        ],
      },
      {
        module: "Lịch bảo trì",
        permissions: ["Xem danh sách lịch bảo trì"],
      },
      {
        module: "Thông báo",
        permissions: ["Xem thông báo"],
      },
    ],
  },

  [ROLE.KHACH_THUE]: {
    roleName: "Khách thuê",
    description:
      "Theo dõi thông tin thuê mặt bằng, công nợ, thanh toán và gửi yêu cầu.",
    groups: [
      {
        module: "Dashboard",
        permissions: ["Xem dashboard khách thuê"],
      },
      {
        module: "Mặt bằng",
        permissions: [
          "Xem thông tin mặt bằng đang thuê",
          "Xem tình trạng mặt bằng liên quan",
        ],
      },
      {
        module: "Hợp đồng",
        permissions: [
          "Xem hợp đồng thuê của mình",
          "Xem chi tiết hợp đồng thuê",
        ],
      },
      {
        module: "Yêu cầu thuê thêm",
        permissions: [
          "Xem yêu cầu thuê thêm của mình",
          "Gửi yêu cầu thuê thêm mặt bằng",
          "Theo dõi trạng thái yêu cầu thuê thêm",
        ],
      },
      {
        module: "Công nợ",
        permissions: [
          "Xem công nợ của mình",
          "Theo dõi trạng thái công nợ",
        ],
      },
      {
        module: "Thanh toán",
        permissions: [
          "Tạo giao dịch thanh toán công nợ",
          "Mô phỏng thanh toán",
          "Xem kết quả giao dịch thanh toán",
        ],
      },
      {
        module: "Sự cố bảo trì",
        permissions: [
          "Xem danh sách sự cố đã gửi",
          "Gửi yêu cầu xử lý sự cố bảo trì",
          "Theo dõi trạng thái xử lý sự cố",
        ],
      },
      {
        module: "Thông báo",
        permissions: ["Xem thông báo"],
      },
    ],
  },
};

export default function RbacPage() {
  const [selectedRole, setSelectedRole] = useState(ROLE.QTV);

  const selectedRoleData = useMemo(
    () => ROLE_PERMISSION_GROUPS[selectedRole],
    [selectedRole],
  );

  const totalPermissionCount = useMemo(() => {
    if (!selectedRoleData?.groups) return 0;

    return selectedRoleData.groups.reduce(
      (total, group) => total + group.permissions.length,
      0,
    );
  }, [selectedRoleData]);

  return (
    <>
      <PageHeader
        title="Vai trò và phân quyền"
        subtitle="Xem danh sách chức năng được phép sử dụng theo từng vai trò"
      />

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card title="Danh sách vai trò">
            <List
              dataSource={ROLE_ORDER}
              renderItem={(roleCode) => {
                const isActive = selectedRole === roleCode;
                const roleData = ROLE_PERMISSION_GROUPS[roleCode];

                return (
                  <List.Item
                    onClick={() => setSelectedRole(roleCode)}
                    style={{
                      cursor: "pointer",
                      borderRadius: 8,
                      padding: 12,
                      marginBottom: 8,
                      background: isActive ? "#f0f5ff" : undefined,
                      border: isActive
                        ? "1px solid #adc6ff"
                        : "1px solid transparent",
                    }}
                  >
                    <List.Item.Meta
                      title={
                        <Space direction="vertical" size={2}>
                          <Text strong>
                            {ROLE_LABEL[roleCode] ||
                              roleData?.roleName ||
                              roleCode}
                          </Text>
                          <Text type="secondary">{roleCode}</Text>
                        </Space>
                      }
                      description={roleData?.description}
                    />
                  </List.Item>
                );
              }}
            />
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card
            title="Danh sách chức năng"
            extra={
              <Space>
                <Tag>{selectedRole}</Tag>
                <Tag color="blue">{totalPermissionCount} quyền</Tag>
              </Space>
            }
          >
            {selectedRoleData ? (
              <>
                <Space
                  direction="vertical"
                  size={4}
                  style={{ width: "100%", marginBottom: 16 }}
                >
                  <Text strong style={{ fontSize: 18 }}>
                    {ROLE_LABEL[selectedRole] || selectedRoleData.roleName}
                  </Text>
                  <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                    {selectedRoleData.description}
                  </Paragraph>
                </Space>

                <Space direction="vertical" size={16} style={{ width: "100%" }}>
                  {selectedRoleData.groups.map((group) => (
                    <Card
                      key={group.module}
                      size="small"
                      title={
                        <Space>
                          <Text strong>{group.module}</Text>
                          <Tag>{group.permissions.length} quyền</Tag>
                        </Space>
                      }
                    >
                      <List
                        dataSource={group.permissions}
                        renderItem={(permission) => (
                          <List.Item>
                            <Space align="start">
                              <CheckCircleOutlined
                                style={{ color: "#52c41a", marginTop: 4 }}
                              />
                              <Text>{permission}</Text>
                            </Space>
                          </List.Item>
                        )}
                      />
                    </Card>
                  ))}
                </Space>
              </>
            ) : (
              <Empty description="Chưa có danh sách quyền cho vai trò này" />
            )}
          </Card>
        </Col>
      </Row>
    </>
  );
}