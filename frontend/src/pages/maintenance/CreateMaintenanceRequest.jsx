import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Form,
  Input,
  Select,
  Button,
  Space,
  message,
  Spin,
} from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { createTicket } from '../../services/maintenanceService';
import { MAINTENANCE_CATEGORIES } from '../../constants/maintenanceConstants';

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

export default function CreateMaintenanceRequest() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const basePath = '/staff/maintenance';

  const handleBack = () => {
    navigate(basePath);
  };

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const ticketData = {
        title: values.title,
        description: values.description,
        location: values.location,
        category: values.category,
        priority: values.priority || 'medium',
      };

      const result = await createTicket(ticketData);
      message.success('Tạo yêu cầu bảo trì thành công');
      navigate(`${basePath}/${result.id}`);
    } catch (error) {
      message.error('Tạo yêu cầu thất bại');
    } finally {
      setLoading(false);
    }
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

      <Card bordered={false} style={{ borderRadius: 8, maxWidth: 800 }}>
        <Title level={4} style={{ marginBottom: 24 }}>
          Tạo yêu cầu bảo trì mới
        </Title>

        <Spin spinning={loading}>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
          >
            <Form.Item
              name="title"
              label="Tiêu đề yêu cầu"
              rules={[
                { required: true, message: 'Vui lòng nhập tiêu đề' },
                { max: 200, message: 'Tiêu đề không quá 200 ký tự' },
              ]}
            >
              <Input placeholder="VD: Máy lạnh không hoạt động" />
            </Form.Item>

            <Form.Item
              name="description"
              label="Mô tả chi tiết"
              rules={[
                { required: true, message: 'Vui lòng mô tả chi tiết vấn đề' },
              ]}
            >
              <TextArea
                rows={5}
                placeholder="Mô tả chi tiết vấn đề, triệu chứng, và nơi xảy ra..."
              />
            </Form.Item>

            <Form.Item
              name="location"
              label="Vị trí/Mặt bằng"
              rules={[
                { required: true, message: 'Vui lòng nhập vị trí' },
              ]}
            >
              <Input placeholder="VD: GF-01, L2-12" />
            </Form.Item>

            <Form.Item
              name="category"
              label="Loại yêu cầu"
              rules={[
                { required: true, message: 'Vui lòng chọn loại yêu cầu' },
              ]}
            >
              <Select placeholder="Chọn loại yêu cầu">
                {MAINTENANCE_CATEGORIES.map((category) => (
                  <Option key={category} value={category}>
                    {category}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name="priority"
              label="Ưu tiên"
              initialValue="medium"
              rules={[
                { required: true, message: 'Vui lòng chọn ưu tiên' },
              ]}
            >
              <Select>
                <Option value="low">Thấp - Có thể xử lý sau</Option>
                <Option value="medium">Trung bình - Trong vài ngày</Option>
                <Option value="high">Cao - Trong 24 giờ</Option>
                <Option value="urgent">Khẩn cấp - Ngay lập tức</Option>
              </Select>
            </Form.Item>

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit" loading={loading}>
                  Gửi yêu cầu
                </Button>
                <Button onClick={handleBack}>Hủy</Button>
              </Space>
            </Form.Item>
          </Form>
        </Spin>
      </Card>
    </div>
  );
}
