import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Typography,
  Card,
  Button,
  Space,
  Descriptions,
  Spin,
  message,
  Tag,
  Select,
  Divider,
  Timeline,
  Form,
  Modal,
  Row,
  Col,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import {
  getTicketById,
  updateTicketStatus,
  assignTicket,
} from '../../services/maintenanceService';
import {
  TICKET_STATUS_LABELS,
  TICKET_STATUS_COLORS,
  TICKET_PRIORITY_LABELS,
  TICKET_PRIORITY_COLORS,
} from '../../constants/maintenanceConstants';
import { formatDate } from '../../utils/format';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

export default function MaintenanceDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState(null);
  const [selectedAssignee, setSelectedAssignee] = useState(null);

  const basePath = '/staff/maintenance';

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const data = await getTicketById(id);
        if (!cancelled) {
          setTicket(data);
          setSelectedStatus(data.status);
          setSelectedAssignee(data.assigned_to);
        }
      } catch (error) {
        if (!cancelled) {
          message.error('Không tải được thông tin yêu cầu');
          navigate(basePath);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [id, navigate, basePath]);

  const handleBack = () => {
    navigate(basePath);
  };

  const handleUpdateStatus = async () => {
    if (!selectedStatus) {
      message.warning('Vui lòng chọn trạng thái');
      return;
    }
    setUpdating(true);
    try {
      const updated = await updateTicketStatus(id, selectedStatus);
      setTicket(updated);
      message.success('Cập nhật trạng thái thành công');
      setShowStatusModal(false);
    } catch (error) {
      message.error('Cập nhật trạng thái thất bại');
    } finally {
      setUpdating(false);
    }
  };

  const handleAssignTicket = async () => {
    if (!selectedAssignee) {
      message.warning('Vui lòng chọn người xử lý');
      return;
    }
    setUpdating(true);
    try {
      const updated = await assignTicket(id, selectedAssignee);
      setTicket(updated);
      message.success('Gán yêu cầu thành công');
      setShowAssignModal(false);
    } catch (error) {
      message.error('Gán yêu cầu thất bại');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) return <Spin />;
  if (!ticket) return <div>Không tìm thấy yêu cầu</div>;

  return (
    <div>
      <Button
        type="text"
        icon={<ArrowLeftOutlined />}
        onClick={handleBack}
        style={{ marginBottom: 16 }}
      >
        Quay lại
      </Button>

      <Card bordered={false} style={{ borderRadius: 8 }}>
        <div style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <Title level={4} style={{ margin: 0 }}>
              {ticket.title}
            </Title>
            <Tag color={TICKET_STATUS_COLORS[ticket.status]}>
              {TICKET_STATUS_LABELS[ticket.status]}
            </Tag>
          </div>

          <Paragraph type="secondary">{ticket.description}</Paragraph>
        </div>

        <Divider />

        <div style={{ marginBottom: 24 }}>
          <Descriptions column={2} size="small" bordered>
            <Descriptions.Item label="Mã yêu cầu" span={1}>
              <Text strong>{ticket.id}</Text>
            </Descriptions.Item>
            <Descriptions.Item label="Ưu tiên" span={1}>
              <Tag color={TICKET_PRIORITY_COLORS[ticket.priority]}>
                {TICKET_PRIORITY_LABELS[ticket.priority]}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Vị trí" span={1}>
              {ticket.location}
            </Descriptions.Item>
            <Descriptions.Item label="Loại yêu cầu" span={1}>
              {ticket.category}
            </Descriptions.Item>
            <Descriptions.Item label="Ngày tạo" span={1}>
              {formatDate(ticket.created_at)}
            </Descriptions.Item>
            <Descriptions.Item label="Người tạo" span={1}>
              {ticket.created_by}
            </Descriptions.Item>
            <Descriptions.Item label="Người xử lý" span={1}>
              {ticket.assigned_to ? (
                <Text>{ticket.assigned_to}</Text>
              ) : (
                <Text type="secondary">Chưa gán</Text>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="Ngày cập nhật" span={1}>
              {formatDate(ticket.updated_at)}
            </Descriptions.Item>
            {ticket.completion_date && (
              <Descriptions.Item label="Ngày hoàn thành" span={1}>
                {formatDate(ticket.completion_date)}
              </Descriptions.Item>
            )}
          </Descriptions>
        </div>

        <Divider />

        <div style={{ marginBottom: 24 }}>
          <Title level={5}>Lịch sử cập nhật</Title>
          <Timeline
            items={[
              {
                children: `Yêu cầu được tạo bởi ${ticket.created_by} vào ${formatDate(
                  ticket.created_at
                )}`,
              },
              ticket.assigned_to && {
                children: `Gán cho ${ticket.assigned_to}`,
              },
              ticket.status !== 'open' && {
                children: `Trạng thái: ${TICKET_STATUS_LABELS[ticket.status]}`,
              },
            ].filter(Boolean)}
          />
        </div>

        <Space>
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => setShowStatusModal(true)}
          >
            Cập nhật trạng thái
          </Button>
          <Button
            icon={<CheckCircleOutlined />}
            onClick={() => setShowAssignModal(true)}
          >
            Gán yêu cầu
          </Button>
        </Space>
      </Card>

      {/* Status Update Modal */}
      <Modal
        title="Cập nhật trạng thái yêu cầu"
        open={showStatusModal}
        onOk={handleUpdateStatus}
        onCancel={() => setShowStatusModal(false)}
        confirmLoading={updating}
      >
        <Form layout="vertical">
          <Form.Item label="Trạng thái mới">
            <Select
              value={selectedStatus}
              onChange={setSelectedStatus}
              placeholder="Chọn trạng thái"
            >
              <Option value="open">Mở</Option>
              <Option value="in_progress">Đang xử lý</Option>
              <Option value="resolved">Đã giải quyết</Option>
              <Option value="closed">Đóng</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Assign Modal */}
      <Modal
        title="Gán yêu cầu cho nhân viên"
        open={showAssignModal}
        onOk={handleAssignTicket}
        onCancel={() => setShowAssignModal(false)}
        confirmLoading={updating}
      >
        <Form layout="vertical">
          <Form.Item label="Người xử lý">
            <Select
              value={selectedAssignee}
              onChange={setSelectedAssignee}
              placeholder="Chọn nhân viên"
            >
              <Option value="staff@example.com">Staff User</Option>
              <Option value="maintenance@example.com">Maintenance Team</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
