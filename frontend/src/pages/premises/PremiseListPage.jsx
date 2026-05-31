import {
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
  ToolOutlined,
  UndoOutlined,
} from "@ant-design/icons";
import {
  Button,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  message,
} from "antd";
import { useCallback, useState } from "react";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { ROLE } from "../../constants/roles";
import { MAT_BANG_STATUS } from "../../constants/statuses";
import { useAuth } from "../../hooks/useAuth";
import { useCrudList } from "../../hooks/useCrudList";
import { showApiError } from "../../services/apiClient";
import { premiseService } from "../../services/premiseService";
import { pick, pickId } from "../../utils/data";

const STATUS_CON_TRONG = "Còn trống";
const STATUS_DANG_BAO_TRI = "Đang bảo trì";

function getPremiseId(record) {
  return pickId(record, ["ma_mat_bang", "ma_mb", "MAMB"]);
}

function getPremiseStatus(record) {
  return pick(record, ["trang_thai", "TRANGTHAI"]);
}

export default function PremiseListPage() {
  const { role } = useAuth();
  const canWrite = [ROLE.TP_VHBT, ROLE.NV_VHBT].includes(role);

  const [open, setOpen] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [status, setStatus] = useState(undefined);
  const [form] = Form.useForm();

  const fetcher = useCallback((params) => premiseService.list(params), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const search = () => {
    setParams({
      keyword: keyword || undefined,
      trang_thai: status || undefined,
      page: 1,
      page_size: 20,
    });
  };

  const clearAndReload = () => {
    setKeyword("");
    setStatus(undefined);
    setParams({ page: 1, page_size: 20 });
  };

  const create = async () => {
    try {
      const values = await form.validateFields();
      await premiseService.create(values);
      message.success("Tạo mặt bằng thành công");
      setOpen(false);
      form.resetFields();
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const remove = async (record) => {
    try {
      await premiseService.remove(getPremiseId(record));
      message.success("Đã xóa mặt bằng");
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const changeMaintenanceStatus = async (record, nextStatus) => {
    try {
      await premiseService.updateMaintenanceStatus(getPremiseId(record), nextStatus);
      message.success(`Đã chuyển trạng thái mặt bằng sang ${nextStatus}`);
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const renderMaintenanceStatusButton = (record) => {
    const currentStatus = getPremiseStatus(record);

    if (currentStatus === STATUS_CON_TRONG) {
      return (
        <Popconfirm
          title="Chuyển mặt bằng này sang trạng thái Đang bảo trì?"
          okText="Chuyển"
          cancelText="Hủy"
          onConfirm={() => changeMaintenanceStatus(record, STATUS_DANG_BAO_TRI)}
        >
          <Button size="small" icon={<ToolOutlined />}>
            Chuyển bảo trì
          </Button>
        </Popconfirm>
      );
    }

    if (currentStatus === STATUS_DANG_BAO_TRI) {
      return (
        <Popconfirm
          title="Chuyển mặt bằng này về trạng thái Còn trống?"
          okText="Chuyển"
          cancelText="Hủy"
          onConfirm={() => changeMaintenanceStatus(record, STATUS_CON_TRONG)}
        >
          <Button size="small" icon={<UndoOutlined />}>
            Chuyển còn trống
          </Button>
        </Popconfirm>
      );
    }

    return null;
  };

  const columns = [
    {
      title: "Mã",
      render: (_, record) => getPremiseId(record),
    },
    {
      title: "Vị trí",
      render: (_, record) => pick(record, ["vi_tri", "VITRI"]),
    },
    {
      title: "Tầng",
      render: (_, record) => {
        const floor = pick(record, ["tang", "TANG"]);
        return Number(floor) === 0 ? "Trệt" : floor;
      },
    },
    {
      title: "Diện tích",
      render: (_, record) => `${pick(record, ["dien_tich", "DIENTICH"])} m²`,
    },
    {
      title: "Loại",
      render: (_, record) => pick(record, ["loai_mat_bang", "loai_mb", "LOAIMB"]),
    },
    {
      title: "Trạng thái",
      render: (_, record) => <StatusTag value={getPremiseStatus(record)} />,
    },
    {
      title: "Thao tác",
      align: "right",
      render: (_, record) => {
        if (!canWrite) return null;

        return (
          <Space wrap>
            {renderMaintenanceStatusButton(record)}

            <Popconfirm
              title="Xóa mặt bằng này?"
              okText="Xóa"
              cancelText="Hủy"
              onConfirm={() => remove(record)}
            >
              <Button size="small" danger icon={<DeleteOutlined />}>
                Xóa
              </Button>
            </Popconfirm>
          </Space>
        );
      },
    },
  ];

  return (
    <>
      <PageHeader
        title="Mặt bằng"
        subtitle="Quản lý thông tin và trạng thái vận hành mặt bằng"
        actionText={canWrite ? "Thêm mặt bằng" : undefined}
        actionIcon={<PlusOutlined />}
        onAction={canWrite ? () => setOpen(true) : undefined}
      />

      <Space wrap style={{ marginBottom: 16 }}>
        <Input
          allowClear
          prefix={<SearchOutlined />}
          placeholder="Tìm kiếm mã hoặc vị trí mặt bằng"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          onPressEnter={search}
          style={{ width: 320 }}
        />

        <Select
          allowClear
          placeholder="Lọc trạng thái"
          value={status}
          options={MAT_BANG_STATUS.map((item) => ({ value: item, label: item }))}
          onChange={setStatus}
          style={{ width: 220 }}
        />

        <Button type="primary" icon={<SearchOutlined />} onClick={search}>
          Lọc
        </Button>

        <Button icon={<ReloadOutlined />} onClick={clearAndReload}>
          Tải lại
        </Button>
      </Space>

      <ResponsiveTable
        rowKey={(record) => getPremiseId(record)}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title="Tạo mặt bằng"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={create}
        destroyOnClose
        okText="Tạo"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="ma_mat_bang"
            label="Mã mặt bằng"
            rules={[{ required: true, message: "Vui lòng nhập mã mặt bằng" }]}
          >
            <Input placeholder="Ví dụ: MB001" />
          </Form.Item>

          <Form.Item
            name="vi_tri"
            label="Vị trí"
            rules={[{ required: true, message: "Vui lòng nhập vị trí" }]}
          >
            <Input placeholder="Ví dụ: Khu A - Gian 01" />
          </Form.Item>

          <Form.Item
            name="tang"
            label="Tầng"
            rules={[{ required: true, message: "Vui lòng nhập tầng" }]}
          >
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>

          <Form.Item
            name="dien_tich"
            label="Diện tích"
            rules={[{ required: true, message: "Vui lòng nhập diện tích" }]}
          >
            <InputNumber min={1} style={{ width: "100%" }} />
          </Form.Item>

          <Form.Item
            name="loai_mat_bang"
            label="Loại mặt bằng"
            rules={[{ required: true, message: "Vui lòng nhập loại mặt bằng" }]}
          >
            <Input placeholder="Ví dụ: Cửa hàng, Kiosk, Kho" />
          </Form.Item>

          <Form.Item
            name="trang_thai"
            label="Trạng thái"
            rules={[{ required: true, message: "Vui lòng chọn trạng thái" }]}
          >
            <Select
              options={MAT_BANG_STATUS.map((item) => ({ value: item, label: item }))}
            />
          </Form.Item>

          <Form.Item name="ghi_chu" label="Ghi chú">
            <Input.TextArea rows={3} placeholder="Nhập ghi chú nếu có" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
