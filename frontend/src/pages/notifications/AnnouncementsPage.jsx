import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Button,
  Table,
  Space,
  Select,
  Modal,
  Form,
  Input,
  message,
  Spin,
  Tag,
  Row,
  Col,
  Checkbox,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  EyeOutlined,
  RedoOutlined,
} from '@ant-design/icons';
import {
  listAnnouncements,
  createAnnouncement,
  getAnnouncementById,
} from '../../services/notificationService';
import { formatDate } from '../../utils/format';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const ANNOUNCEMENT_STATUSES = {
  draft: { label: 'Nháp', color: 'default' },
  scheduled: { label: 'Lên lịch', color: 'blue' },
  published: { label: 'Đã đăng', color: 'green' },
  archived: { label: 'Lưu trữ', color: 'gray' },
};

export default function AnnouncementsPage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedAnnouncement, setSelectedAnnouncement] = useState(null);
  const [filters, setFilters] = useState({ status: 'published' });
  const [recipients, setRecipients] = useState(['staff', 'tenant']);

  const loadAnnouncements = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.status) params.status = filters.status;

      const response = await listAnnouncements(params);
      const items = Array.isArray(response) ? response : response.items || [];
      setAnnouncements(items);
    } catch (error) {
      message.error('Không thể tải danh sách thông báo');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnnouncements();
  }, [filters.status]);

  const handleCreateAnnouncement = async (values) => {
    setSubmitting(true);
    try {
      const announcementData = {
        title: values.title,
        content: values.content,
        recipients,
        scheduled_at: values.scheduled_at || null,
      };

      await createAnnouncement(announcementData);
      message.success('Tạo thông báo thành công');
      form.resetFields();
      setRecipients(['staff', 'tenant']);
      setShowModal(false);
      loadAnnouncements();
    } catch (error) {
      message.error('Tạo thông báo thất bại');
    } finally {
      setSubmitting(false);
    }
  };

  const handleViewDetail = async (announcement) => {
    setSelectedAnnouncement(announcement);
    setShowDetailModal(true);
  };

  const handleRefresh = () => {
    loadAnnouncements();
  };

  const columns = [
    {
      title: 'Tiêu đề',
      dataIndex: 'title',
      key: 'title',
      width: '35%',
      render: (text) => <Text strong>{text}</Text>,
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => {
        const config = ANNOUNCEMENT_STATUSES[status];
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: 'Người tạo',
      dataIndex: 'created_by',
      key: 'created_by',
      width: 150,
    },
    {
      title: 'Ngày tạo',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 140,
      render: (date) => formatDate(date),
    },
    {
      title: 'Đạo cáo xem',
      dataIndex: 'read_count',
      key: 'read_count',
      width: 100,
      align: 'center',
      render: (count) => <Text strong>{count}</Text>,
    },
    {
      title: 'Hành động',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => handleViewDetail(record)}
          >
            Xem
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Card bordered={false} style={{ borderRadius: 8 }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ marginBottom: 16 }}>
          Ban hành thông báo
        </Title>

        <div style={{ marginBottom: 16 }}>
          <Space wrap>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setShowModal(true)}
            >
              Tạo thông báo
            </Button>
            <Button icon={<RedoOutlined />} onClick={handleRefresh}>
              Làm mới
            </Button>
          </Space>
        </div>

        <div style={{ marginBottom: 16 }}>
          <Select
            style={{ width: 200 }}
            value={filters.status}
            onChange={(value) =>
              setFilters({ ...filters, status: value })
            }
          >
            <Option value="published">Đã đăng</Option>
            <Option value="draft">Nháp</Option>
            <Option value="scheduled">Lên lịch</Option>
            <Option value="archived">Lưu trữ</Option>
          </Select>
        </div>
      </div>

      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={announcements}
          rowKey="id"
          pagination={{ pageSize: 10, total: announcements.length }}
          scroll={{ x: 1000 }}
        />
      </Spin>

      {/* Create Announcement Modal */}
      <Modal
        title="Tạo thông báo mới"
        open={showModal}
        onOk={() => form.submit()}
        onCancel={() => setShowModal(false)}
        confirmLoading={submitting}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateAnnouncement}
        >
          <Form.Item
            name="title"
            label="Tiêu đề"
            rules={[
              { required: true, message: 'Vui lòng nhập tiêu đề' },
            ]}
          >
            <Input placeholder="Nhập tiêu đề thông báo" />
          </Form.Item>

          <Form.Item
            name="content"
            label="Nội dung"
            rules={[
              { required: true, message: 'Vui lòng nhập nội dung' },
            ]}
          >
            <TextArea
              rows={6}
              placeholder="Nhập nội dung thông báo"
            />
          </Form.Item>

          <Form.Item label="Gửi tới">
            <Checkbox.Group
              value={recipients}
              onChange={setRecipients}
              options={[
                { label: 'Admin', value: 'admin' },
                { label: 'Ban quản lý', value: 'management' },
                { label: 'Nhân viên', value: 'staff' },
                { label: 'Khách thuê', value: 'tenant' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="scheduled_at"
            label="Lên lịch (tùy chọn)"
          >
            <Input
              type="datetime-local"
              placeholder="Chọn ngày giờ để lên lịch gửi"
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Detail Modal */}
      <Modal
        title="Chi tiết thông báo"
        open={showDetailModal}
        onCancel={() => setShowDetailModal(false)}
        footer={null}
        width={700}
      >
        {selectedAnnouncement && (
          <div>
            <div style={{ marginBottom: 20 }}>
              <Title level={5}>{selectedAnnouncement.title}</Title>
              <Row gutter={16} style={{ marginBottom: 16 }}>
                <Col>
                  <Text type="secondary">Trạng thái:</Text>{' '}
                  <Tag
                    color={
                      ANNOUNCEMENT_STATUSES[selectedAnnouncement.status]
                        .color
                    }
                  >
                    {
                      ANNOUNCEMENT_STATUSES[selectedAnnouncement.status]
                        .label
                    }
                  </Tag>
                </Col>
                <Col>
                  <Text type="secondary">Đạo cáo xem:</Text>{' '}
                  <Text strong>{selectedAnnouncement.read_count}</Text>
                </Col>
              </Row>
            </div>

            <Paragraph
              style={{
                whiteSpace: 'pre-wrap',
                background: '#f5f5f5',
                padding: 12,
                borderRadius: 4,
                marginBottom: 16,
              }}
            >
              {selectedAnnouncement.content}
            </Paragraph>

            <Row gutter={20}>
              <Col>
                <Text type="secondary">Người tạo:</Text>{' '}
                {selectedAnnouncement.created_by}
              </Col>
              <Col>
                <Text type="secondary">Ngày tạo:</Text>{' '}
                {formatDate(selectedAnnouncement.created_at)}
              </Col>
            </Row>

            {selectedAnnouncement.published_at && (
              <Row gutter={20} style={{ marginTop: 12 }}>
                <Col>
                  <Text type="secondary">Ngày đăng:</Text>{' '}
                  {formatDate(selectedAnnouncement.published_at)}
                </Col>
              </Row>
            )}

            <div style={{ marginTop: 20 }}>
              <Text type="secondary">Gửi tới:</Text>
              <div>
                {selectedAnnouncement.recipients.map((r) => (
                  <Tag key={r} color="blue" style={{ marginTop: 8 }}>
                    {r === 'admin'
                      ? 'Admin'
                      : r === 'management'
                      ? 'Ban quản lý'
                      : r === 'staff'
                      ? 'Nhân viên'
                      : 'Khách thuê'}
                  </Tag>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </Card>
  );
}
