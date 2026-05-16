import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Row,
  Col,
  Button,
  Statistic,
  Spin,
  message,
  Tabs,
  Space,
  Select,
  Table,
  Tag,
} from 'antd';
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { DownloadOutlined } from '@ant-design/icons';
import {
  getKPIDashboard,
  getRevenueReport,
  getDebtReport,
  getOccupancyReport,
} from '../../services/reportsService';
import { formatCurrency } from '../../utils/format';

const { Title, Text } = Typography;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function ReportsDashboard() {
  const navigate = useNavigate();
  const [kpiData, setKpiData] = useState(null);
  const [revenueData, setRevenueData] = useState(null);
  const [debtData, setDebtData] = useState(null);
  const [occupancyData, setOccupancyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('1');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [kpi, revenue, debt, occupancy] = await Promise.all([
        getKPIDashboard(),
        getRevenueReport(),
        getDebtReport(),
        getOccupancyReport(),
      ]);

      setKpiData(kpi);
      setRevenueData(revenue);
      setDebtData(debt);
      setOccupancyData(occupancy);
    } catch (error) {
      message.error('Không thể tải dữ liệu báo cáo');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Spin />;

  return (
    <div style={{ padding: '0' }}>
      <Card bordered={false} style={{ borderRadius: 8, marginBottom: 16 }}>
        <Title level={4} style={{ marginBottom: 16 }}>
          Báo cáo tổng hợp
        </Title>

        {/* KPI Cards */}
        {kpiData && (
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card size="small" bordered={false}>
                <Statistic
                  title="Doanh thu tháng này"
                  value={kpiData.key_metrics.current_month_revenue}
                  formatter={(value) => formatCurrency(value)}
                  valueStyle={{ color: '#1890ff', fontSize: '20px' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card size="small" bordered={false}>
                <Statistic
                  title="Công nợ còn lại"
                  value={kpiData.key_metrics.total_outstanding_debt}
                  formatter={(value) => formatCurrency(value)}
                  valueStyle={{ color: '#f5222d', fontSize: '20px' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card size="small" bordered={false}>
                <Statistic
                  title="Tỷ lệ lấp đầy"
                  value={kpiData.key_metrics.occupancy_rate}
                  suffix="%"
                  valueStyle={{ color: '#52c41a', fontSize: '20px' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card size="small" bordered={false}>
                <Statistic
                  title="Khoản quá hạn"
                  value={kpiData.key_metrics.overdue_items}
                  valueStyle={{ color: '#fa8c16', fontSize: '20px' }}
                />
              </Card>
            </Col>
          </Row>
        )}
      </Card>

      <Card bordered={false} style={{ borderRadius: 8 }}>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: '1',
              label: 'Doanh thu',
              children: revenueData && (
                <div>
                  <Row gutter={16} style={{ marginBottom: 20 }}>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Tổng doanh thu"
                          value={revenueData.summary.total_revenue}
                          formatter={(value) => formatCurrency(value)}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Tiền thuê"
                          value={revenueData.summary.total_rent}
                          formatter={(value) => formatCurrency(value)}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Dịch vụ"
                          value={revenueData.summary.total_service}
                          formatter={(value) => formatCurrency(value)}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Bình quân hàng tháng"
                          value={revenueData.summary.avg_monthly_revenue}
                          formatter={(value) => formatCurrency(value)}
                        />
                      </Card>
                    </Col>
                  </Row>

                  <div style={{ background: '#fff', borderRadius: 8, padding: 16 }}>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={revenueData.data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip
                          formatter={(value) => formatCurrency(value)}
                        />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="total_revenue"
                          stroke="#1890ff"
                          name="Tổng doanh thu"
                        />
                        <Line
                          type="monotone"
                          dataKey="rent_revenue"
                          stroke="#52c41a"
                          name="Tiền thuê"
                        />
                        <Line
                          type="monotone"
                          dataKey="service_revenue"
                          stroke="#faad14"
                          name="Dịch vụ"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              ),
            },
            {
              key: '2',
              label: 'Công nợ',
              children: debtData && (
                <div>
                  <Row gutter={16} style={{ marginBottom: 20 }}>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Tổng công nợ"
                          value={debtData.summary.total_outstanding}
                          formatter={(value) => formatCurrency(value)}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Khoản quá hạn"
                          value={debtData.summary.total_overdue_items}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Ngày quá hạn TB"
                          value={debtData.summary.avg_overdue_days}
                          suffix=" ngày"
                        />
                      </Card>
                    </Col>
                  </Row>

                  <Table
                    columns={[
                      { title: 'Khách thuê', dataIndex: 'tenant', key: 'tenant' },
                      { title: 'Mặt bằng', dataIndex: 'premise', key: 'premise' },
                      {
                        title: 'Còn lại',
                        dataIndex: 'outstanding_amount',
                        key: 'outstanding_amount',
                        render: (v) => formatCurrency(v),
                      },
                      {
                        title: 'Quá hạn',
                        dataIndex: 'overdue_days',
                        key: 'overdue_days',
                        render: (v) => (
                          <Tag color={v > 0 ? 'red' : 'green'}>
                            {v} ngày
                          </Tag>
                        ),
                      },
                      {
                        title: 'Trạng thái',
                        dataIndex: 'status',
                        key: 'status',
                        render: (s) => (
                          <Tag color={s === 'overdue' ? 'red' : 'green'}>
                            {s === 'overdue' ? 'Quá hạn' : 'Đã thanh toán'}
                          </Tag>
                        ),
                      },
                    ]}
                    dataSource={debtData.data}
                    rowKey="tenant"
                    pagination={{ pageSize: 5 }}
                  />
                </div>
              ),
            },
            {
              key: '3',
              label: 'Lấp đầy',
              children: occupancyData && (
                <div>
                  <Row gutter={16} style={{ marginBottom: 20 }}>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Mặt bằng có"
                          value={occupancyData.summary.total_premises}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Đã cho thuê"
                          value={occupancyData.summary.occupied}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Còn trống"
                          value={occupancyData.summary.vacant}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card size="small" bordered={false}>
                        <Statistic
                          title="Tỷ lệ lấp đầy"
                          value={occupancyData.summary.occupancy_rate.toFixed(1)}
                          suffix="%"
                        />
                      </Card>
                    </Col>
                  </Row>

                  <Title level={5} style={{ marginTop: 20, marginBottom: 16 }}>
                    Theo tầng
                  </Title>
                  <Table
                    columns={[
                      { title: 'Tầng', dataIndex: 'floor', key: 'floor' },
                      { title: 'Tổng', dataIndex: 'total', key: 'total' },
                      {
                        title: 'Cho thuê',
                        dataIndex: 'occupied',
                        key: 'occupied',
                      },
                      {
                        title: 'Tỷ lệ',
                        dataIndex: 'occupancy_rate',
                        key: 'occupancy_rate',
                        render: (v) => `${v.toFixed(1)}%`,
                      },
                    ]}
                    dataSource={occupancyData.by_floor}
                    rowKey="floor"
                    pagination={false}
                    style={{ marginBottom: 24 }}
                  />

                  <Title level={5} style={{ marginBottom: 16 }}>
                    Theo loại hình
                  </Title>
                  <Table
                    columns={[
                      {
                        title: 'Loại hình',
                        dataIndex: 'category',
                        key: 'category',
                      },
                      { title: 'Số lượng', dataIndex: 'count', key: 'count' },
                      {
                        title: 'Tỷ lệ',
                        dataIndex: 'occupancy_rate',
                        key: 'occupancy_rate',
                        render: (v) => `${v.toFixed(1)}%`,
                      },
                    ]}
                    dataSource={occupancyData.by_category}
                    rowKey="category"
                    pagination={false}
                  />
                </div>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}
