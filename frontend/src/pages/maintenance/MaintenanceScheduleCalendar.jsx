import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Button,
  Calendar,
  Tag,
  List,
  Spin,
  message,
  Modal,
  Space,
} from 'antd';
import { ArrowLeftOutlined, CloseOutlined } from '@ant-design/icons';
import { listSchedule } from '../../services/maintenanceService';
import { formatDate } from '../../utils/format';

const { Title, Text } = Typography;

export default function MaintenanceScheduleCalendar() {
  const navigate = useNavigate();
  const [scheduleEvents, setScheduleEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(null);
  const [dayEvents, setDayEvents] = useState([]);

  const basePath = '/staff/maintenance';

  useEffect(() => {
    loadSchedule();
  }, []);

  const loadSchedule = async () => {
    setLoading(true);
    try {
      const response = await listSchedule({ limit: 100 });
      const items = Array.isArray(response) ? response : response.items || [];
      setScheduleEvents(items);
    } catch (error) {
      message.error('Không thể tải lịch bảo trì');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate(basePath);
  };

  const getEventsByDate = (date) => {
    if (!date) return [];
    const dateStr = date.format('YYYY-MM-DD');
    return scheduleEvents.filter((event) => event.date === dateStr);
  };

  const handleDateSelect = (date) => {
    setSelectedDate(date);
    const events = getEventsByDate(date);
    setDayEvents(events);
    
    if (events.length > 0) {
      Modal.info({
        title: `Lịch bảo trì ngày ${date.format('DD/MM/YYYY')}`,
        content: (
          <List
            dataSource={events}
            renderItem={(event) => (
              <List.Item key={event.id}>
                <List.Item.Meta
                  title={
                    <div>
                      <Text strong>{event.title}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {event.time}
                      </Text>
                    </div>
                  }
                  description={`${event.location} - ${event.type}`}
                />
              </List.Item>
            )}
          />
        ),
        okText: 'Đóng',
      });
    }
  };

  const cellRender = (date) => {
    const events = getEventsByDate(date);
    return (
      <div style={{ height: '100%' }}>
        {events.length > 0 && (
          <div style={{ fontSize: '12px' }}>
            <Tag color="blue">{events.length} sự kiện</Tag>
          </div>
        )}
      </div>
    );
  };

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
        <Title level={4} style={{ marginBottom: 24 }}>
          Lịch bảo trì & bảo dưỡng
        </Title>

        <Spin spinning={loading}>
          <div style={{ background: '#fff', borderRadius: 8, padding: 16 }}>
            <Calendar
              fullscreen={true}
              onSelect={handleDateSelect}
              cellRender={cellRender}
            />
          </div>
        </Spin>

        {selectedDate && dayEvents.length > 0 && (
          <Card
            title={`Sự kiện ngày ${selectedDate.format('DD/MM/YYYY')}`}
            style={{ marginTop: 24 }}
          >
            <List
              dataSource={dayEvents}
              renderItem={(event) => (
                <List.Item key={event.id}>
                  <List.Item.Meta
                    title={
                      <div>
                        <Text strong>{event.title}</Text>
                        <Tag color="blue" style={{ marginLeft: 8 }}>
                          {event.type}
                        </Tag>
                      </div>
                    }
                    description={
                      <div>
                        <div>
                          <Text type="secondary">Thời gian: {event.time}</Text>
                        </div>
                        <div>
                          <Text type="secondary">Địa điểm: {event.location}</Text>
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        )}

        {/* Upcoming Events Summary */}
        <Card title="Sự kiện sắp tới" style={{ marginTop: 24 }}>
          {scheduleEvents.length > 0 ? (
            <List
              dataSource={scheduleEvents.slice(0, 5)}
              renderItem={(event) => (
                <List.Item key={event.id}>
                  <List.Item.Meta
                    title={
                      <div>
                        <Text strong>{event.title}</Text>
                        <Tag color="green" style={{ marginLeft: 8 }}>
                          {event.date}
                        </Tag>
                      </div>
                    }
                    description={`${event.time} - ${event.location}`}
                  />
                </List.Item>
              )}
            />
          ) : (
            <Text type="secondary">Không có sự kiện nào được lên lịch</Text>
          )}
        </Card>
      </Card>
    </div>
  );
}
