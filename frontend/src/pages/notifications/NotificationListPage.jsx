import { PlusOutlined } from "@ant-design/icons";
import {
  Button,
  Drawer,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Typography,
  message,
} from "antd";
import { useCallback, useState } from "react";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { DOI_TUONG_NHAN, LOAI_THONG_BAO } from "../../constants/statuses";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { notificationService } from "../../services/notificationService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { formatDate, pick, pickId } from "../../utils/data";

const { Title, Paragraph, Text } = Typography;

export default function NotificationListPage() {
  const { role } = useAuth();
  const canCreate = role === ROLE.BQL;
  const [open, setOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selected, setSelected] = useState(null);
  const [form] = Form.useForm();

  const fetcher = useCallback((params) => notificationService.list(params), []);
  const { items, loading, reload } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const create = async () => {
    try {
      const values = await form.validateFields();
      await notificationService.create(values);
      message.success("Đã ban hành thông báo");
      setOpen(false);
      form.resetFields();
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const revoke = async (row) => {
    try {
      await notificationService.revoke(
        pickId(row, ["ma_thong_bao", "ma_tb", "MATB"]),
        { ly_do: "Thu hồi từ giao diện quản lý" },
      );
      message.success("Đã thu hồi thông báo");
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const viewDetail = async (row) => {
    const id = pickId(row, ["ma_thong_bao", "ma_tb", "MATB"]);
    setSelected(row);
    setDetailOpen(true);

    try {
      const detail = await notificationService.detail(id);
      setSelected(detail || row);
    } catch {
      setSelected(row);
    }
  };

  const columns = [
    {
      title: "Tiêu đề",
      render: (_, record) => pick(record, ["tieu_de", "TIEUDE"]),
    },
    {
      title: "Loại",
      render: (_, record) => pick(record, ["loai_thong_bao", "LOAITHONGBAO"]),
    },
    {
      title: "Đối tượng",
      render: (_, record) => pick(record, ["doi_tuong_nhan", "DOITUONGNHAN"]),
    },
    {
      title: "Ngày ban hành",
      render: (_, record) => formatDate(pick(record, ["ngay_ban_hanh", "NGAYBANHANH"])),
    },
    {
      title: "Trạng thái",
      render: (_, record) => <StatusTag value={pick(record, ["trang_thai", "TRANGTHAI"])} />,
    },
    {
      title: "Thao tác",
      align: "right",
      render: (_, record) => (
        <Space>
          <Button type="link" onClick={() => viewDetail(record)}>
            Xem nội dung
          </Button>
          {canCreate && pick(record, ["trang_thai", "TRANGTHAI"]) === "Đã ban hành" ? (
            <Button danger type="link" onClick={() => revoke(record)}>
              Thu hồi
            </Button>
          ) : null}
        </Space>
      ),
    },
  ];

  return (
    <>
      <PageHeader
        title="Thông báo"
        breadcrumb={["Thông báo"]}
        actionText={canCreate ? "Ban hành" : undefined}
        actionIcon={canCreate ? <PlusOutlined /> : undefined}
        onAction={canCreate ? () => setOpen(true) : undefined}
      />

      <ResponsiveTable
        rowKey={(record) => pickId(record, ["ma_thong_bao", "ma_tb", "MATB"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Drawer
        title="Nội dung thông báo"
        open={detailOpen}
        onClose={() => setDetailOpen(false)}
        width={520}
      >
        {selected ? (
          <Space direction="vertical" size={12} style={{ width: "100%" }}>
            <Title level={4}>{pick(selected, ["tieu_de", "TIEUDE"])}</Title>
            <Text type="secondary">
              {pick(selected, ["loai_thong_bao", "LOAITHONGBAO"])} · {pick(selected, ["doi_tuong_nhan", "DOITUONGNHAN"])}
            </Text>
            <StatusTag value={pick(selected, ["trang_thai", "TRANGTHAI"])} />
            <Paragraph className="notification-content">
              {pick(selected, ["noi_dung", "NOIDUNG"], "Không có nội dung")}
            </Paragraph>
          </Space>
        ) : null}
      </Drawer>

      <Modal title="Ban hành thông báo" open={open} onCancel={() => setOpen(false)} onOk={create} okText="Ban hành">
        <Form form={form} layout="vertical">
          <Form.Item label="Tiêu đề" name="tieu_de" rules={[{ required: true, message: "Nhập tiêu đề" }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Loại thông báo" name="loai_thong_bao" rules={[{ required: true, message: "Chọn loại" }]}>
            <Select options={LOAI_THONG_BAO.map((value) => ({ value, label: value }))} />
          </Form.Item>
          <Form.Item label="Đối tượng nhận" name="doi_tuong_nhan" rules={[{ required: true, message: "Chọn đối tượng" }]}>
            <Select options={DOI_TUONG_NHAN.map((value) => ({ value, label: value }))} />
          </Form.Item>
          <Form.Item label="Nội dung" name="noi_dung" rules={[{ required: true, message: "Nhập nội dung" }]}>
            <Input.TextArea rows={5} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
