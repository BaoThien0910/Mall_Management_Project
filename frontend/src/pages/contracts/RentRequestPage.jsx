import { CheckOutlined, CloseOutlined, PlusOutlined } from "@ant-design/icons";
import {
  Button,
  Descriptions,
  Form,
  Input,
  Modal,
  Select,
  Space,
  message,
} from "antd";
import { useCallback, useEffect, useState } from "react";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { useCrudList } from "../../hooks/useCrudList";
import { rentRequestService } from "../../services/rentRequestService";
import { lookupService } from "../../services/lookupService";
import { showApiError } from "../../services/apiClient";
import { pick, pickId, formatDate, toArray } from "../../utils/data";

function getPremiseId(record) {
  return pick(record, ["ma_mat_bang", "ma_mb", "MAMB"], undefined);
}

export default function RentRequestPage() {
  const { role } = useAuth();
  const isTenant = role === ROLE.KHACH_THUE;

  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();
  const [vacantPremises, setVacantPremises] = useState([]);
  const [selectedPremise, setSelectedPremise] = useState(null);

  const fetcher = useCallback(
    (params) => (isTenant ? rentRequestService.myRequests(params) : rentRequestService.list(params)),
    [isTenant],
  );

  const { items, loading, reload } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const loadVacantPremises = useCallback(async () => {
    try {
      const data = await lookupService.vacantPremises();
      setVacantPremises(toArray(data));
    } catch (error) {
      showApiError(error);
    }
  }, []);

  useEffect(() => {
    if (isTenant && open) {
      loadVacantPremises();
    }
  }, [isTenant, open, loadVacantPremises]);

  const openCreateModal = () => {
    form.resetFields();
    setSelectedPremise(null);
    setOpen(true);
  };

  const handlePremiseChange = (value) => {
    const premise = vacantPremises.find((item) => getPremiseId(item) === value);
    setSelectedPremise(premise || null);
  };

  const create = async () => {
    try {
      const values = await form.validateFields();

      await rentRequestService.create(values);

      message.success("Đã gửi yêu cầu thuê thêm");
      setOpen(false);
      form.resetFields();
      setSelectedPremise(null);
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const review = async (row, ketQua) => {
    try {
      const payload = { ket_qua: ketQua };

      if (ketQua === "TU_CHOI") {
        payload.ly_do_tu_choi = "Không đáp ứng điều kiện thuê thêm";
      } else {
        payload.ghi_chu_cho_kdtc = "Chuyển sang số hóa hợp đồng";
      }

      await rentRequestService.review(
        pickId(row, ["ma_yeu_cau", "ma_yc", "MAYC"]),
        payload,
      );

      message.success("Đã xử lý yêu cầu");
      reload();
    } catch (error) {
      showApiError(error);
    }
  };

  const premiseOptions = vacantPremises
    .map((item) => {
      const value = getPremiseId(item);
      const viTri = pick(item, ["vi_tri", "VITRI"], "");
      const dienTich = pick(item, ["dien_tich", "DIENTICH"], "");
      const tang = pick(item, ["tang", "TANG"], "");

      return {
        value,
        label: `${value} - ${viTri} - Tầng ${tang} (${dienTich} m²)`,
      };
    })
    .filter((item) => item.value);

  const columns = [
    {
      title: "Mã YC",
      render: (_, record) => pick(record, ["ma_yeu_cau", "ma_yc", "MAYC"]),
    },
    {
      title: "Khách thuê",
      render: (_, record) => pick(record, ["ma_khach_thue", "ma_kh", "MAKH"]),
    },
    {
      title: "Mặt bằng",
      render: (_, record) => pick(record, ["ma_mat_bang", "ma_mb", "MAMB"]),
    },
    {
      title: "Ngày gửi",
      render: (_, record) => formatDate(pick(record, ["ngay_gui", "NGAYGUI"])),
    },
    {
      title: "Lý do",
      render: (_, record) => pick(record, ["ly_do", "LYDO"]),
    },
    {
      title: "Trạng thái",
      render: (_, record) => <StatusTag value={pick(record, ["trang_thai", "TRANGTHAI"])} />,
    },
    {
      title: "Thao tác",
      align: "right",
      render: (_, record) =>
        !isTenant && pick(record, ["trang_thai", "TRANGTHAI"]) === "Chờ duyệt" ? (
          <Space>
            <Button
              size="small"
              icon={<CheckOutlined />}
              onClick={() => review(record, "DUYET")}
            >
              Duyệt
            </Button>
            <Button
              size="small"
              danger
              icon={<CloseOutlined />}
              onClick={() => review(record, "TU_CHOI")}
            >
              Từ chối
            </Button>
          </Space>
        ) : null,
    },
  ];

  return (
    <>
      <PageHeader
        title="Yêu cầu thuê thêm"
        subtitle="Gửi và theo dõi yêu cầu thuê thêm mặt bằng"
        actionText={isTenant ? "Gửi yêu cầu" : undefined}
        actionIcon={<PlusOutlined />}
        onAction={isTenant ? openCreateModal : undefined}
      />

      <ResponsiveTable
        rowKey={(record) => pickId(record, ["ma_yeu_cau", "ma_yc", "MAYC"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />

      <Modal
        title="Gửi yêu cầu thuê thêm"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={create}
        destroyOnClose
        okText="Gửi yêu cầu"
        cancelText="Hủy"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="ma_mat_bang"
            label="Mặt bằng thuê thêm"
            rules={[{ required: true, message: "Vui lòng chọn mặt bằng thuê thêm" }]}
          >
            <Select
              showSearch
              placeholder="Chọn mặt bằng còn trống"
              optionFilterProp="label"
              onChange={handlePremiseChange}
              options={premiseOptions}
            />
          </Form.Item>

          {selectedPremise ? (
            <Descriptions bordered size="small" column={1} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Vị trí">
                {pick(selectedPremise, ["vi_tri", "VITRI"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Tầng">
                {pick(selectedPremise, ["tang", "TANG"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Diện tích">
                {pick(selectedPremise, ["dien_tich", "DIENTICH"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Loại mặt bằng">
                {pick(selectedPremise, ["loai_mat_bang", "LOAIMB"], "-")}
              </Descriptions.Item>
              <Descriptions.Item label="Trạng thái">
                {pick(selectedPremise, ["trang_thai", "TRANGTHAI"], "-")}
              </Descriptions.Item>
            </Descriptions>
          ) : null}

          <Form.Item
            name="ly_do"
            label="Lý do thuê thêm"
            rules={[{ required: true, message: "Vui lòng nhập lý do thuê thêm" }]}
          >
            <Input.TextArea rows={4} placeholder="Nhập lý do thuê thêm" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
