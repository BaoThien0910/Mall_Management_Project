import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Button,
  Table,
  Space,
  Select,
  Input,
  Row,
  Col,
  message,
  Tag,
  Statistic,
  Spin,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  RedoOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import {
  listTickets,
  getStatistics,
} from '../../services/maintenanceService';
import {
  TICKET_STATUS_LABELS,
  TICKET_STATUS_COLORS,
  TICKET_PRIORITY_LABELS,
  TICKET_PRIORITY_COLORS,
} from '../../constants/maintenanceConstants';
import { formatDate } from '../../utils/format';

const { Title, Text } = Typography;
const { Option } = Select;

export default function MaintenanceDashboard() {
  const navigate = useNavigate();
  const [tickets, setTickets] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: undefined,
    priority: undefined,
    search: '',
  });

  const basePath = '/staff/maintenance';

  const loadTickets = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;

      const response = await listTickets(params);
      const items = Array.isArray(response) ? response : response.items || [];
      setTickets(items);
    } catch (error) {
      message.error('Không thể tải danh sách yêu cầu bảo trì');
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const stats = await getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  };

  useEffect(() => {
    loadTickets();
    loadStatistics();
  }, [filters.status, filters.priority]);

  const handleViewDetail = (ticketId) => {
    navigate(`${basePath}/${ticketId}`);
  };

  const handleCreateTicket = () => {
    navigate(`${basePath}/new`);
  };

  const handleRefresh = () => {
    loadTickets();
    loadStatistics();
  };

  const handleViewSchedule = () => {
    navigate(`${basePath}/schedule`);
  };

  const columns = [
    {
      title: 'Mã yêu cầu',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      sorter: (a, b) => a.id.localeCompare(b.id),
      render: (text) => <Text strong>{text}</Text>,
    },
    {
      title: 'Tiêu đề',
      dataIndex: 'title',
      key: 'title',
      render: (text) => <Text>{text}</Text>,
    },
    {
      title: 'Vị trí',
      dataIndex: 'location',
      key: 'location',
      width: 120,
    },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      width: 130,
      render: (status) => (
        <Tag color={TICKET_STATUS_COLORS[status]}>
          {TICKET_STATUS_LABELS[status]}
        </Tag>
      ),
    },
    {
      title: 'Ưu tiên',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority) => (
        <Tag color={TICKET_PRIORITY_COLORS[priority]}>
          {TICKET_PRIORITY_LABELS[priority]}
        </Tag>
      ),
    },
    {
      title: 'Ngày tạo',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 130,
      render: (date) => formatDate(date),
    },
    {
      title: 'Người xử lý',
      dataIndex: 'assigned_to',
      key: 'assigned_to',
      width: 150,
      render: (assigned) => assigned ? <Text>{assigned}</Text> : <Text type="secondary">Chưa gán</Text>,
    },
    {
      title: 'Hành động',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button
          type="link"
          onClick={() => handleViewDetail(record.id)}
          size="small"
        >
          Xem chi tiết
        </Button>
      ),
    },
  ];

  return (
    <Card bordered={false} style={{ borderRadius: 8 }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={4} style={{ marginBottom: 16 }}>
          Vận hành & Bảo trì
        </Title>

        {/* Statistics Cards */}
        {statistics && (
          <Row gutter={16} style={{ marginBottom: 20 }}>
            <Col xs={12} sm={12} md={6}>
              <Card size="small" bordered={false}>
                <Statistic
                  title="Tổng yêu cầu"
                  value={statistics.total}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={12} md={6}>
              <Card size="small" bordered={false}>
                <Statistic
                  title="Mở"
                  value={statistics.open}
                  valueStyle={{ color: '#f5222d' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={12} md={6}>
              <Card size="small" bordered={false}>
                <Statistic
                  title="Đang xử lý"
                  value={statistics.in_progress}
                  valueStyle={{ color: '#fa8c16' }}
                />
              </Card>
            </Col>
            <Col xs={12} sm={12} md={6}>
              <Card size="small" bordered={false}>
                <Statistic
                  title="Hoàn thành"
                  value={statistics.resolved + statistics.closed}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
          </Row>
        )}
      </div>

      {/* Filters and Actions */}
      <div style={{ marginBottom: 16 }}>
        <Space wrap>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateTicket}
          >
            Tạo yêu cầu
          </Button>
          <Button
            icon={<CalendarOutlined />}
            onClick={handleViewSchedule}
          >
            Lịch bảo trì
          </Button>
          <Button
            icon={<RedoOutlined />}
            onClick={handleRefresh}
          >
            Làm mới
          </Button>
        </Space>
      </div>

      {/* Filter Controls */}
      <div style={{ marginBottom: 16 }}>
        <Row gutter={12}>
          <Col xs={24} sm={24} md={8}>
            <Select
              placeholder="Lọc theo trạng thái"
              allowClear
              value={filters.status}
              onChange={(value) =>
                setFilters({ ...filters, status: value })
              }
              style={{ width: '100%' }}
            >
              <Option value="open">Mở</Option>
              <Option value="in_progress">Đang xử lý</Option>
              <Option value="resolved">Đã giải quyết</Option>
              <Option value="closed">Đóng</Option>
            </Select>
          </Col>
          <Col xs={24} sm={24} md={8}>
            <Select
              placeholder="Lọc theo ưu tiên"
              allowClear
              value={filters.priority}
              onChange={(value) =>
                setFilters({ ...filters, priority: value })
              }
              style={{ width: '100%' }}
            >
              <Option value="low">Thấp</Option>
              <Option value="medium">Trung bình</Option>
              <Option value="high">Cao</Option>
              <Option value="urgent">Khẩn cấp</Option>
            </Select>
          </Col>
        </Row>
      </div>

      {/* Table */}
      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={tickets}
          rowKey="id"
          pagination={{ pageSize: 10, total: tickets.length }}
          scroll={{ x: 1000 }}
        />
      </Spin>
    </Card>
  );
}
