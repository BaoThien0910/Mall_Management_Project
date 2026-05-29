import { CheckOutlined, CloseOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Form, Input, Modal, Space, message, Select } from "antd";
import { useCallback, useState, useEffect } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { useCrudList } from "../../hooks/useCrudList";
import { rentRequestService } from "../../services/rentRequestService";
import { premiseService } from "../../services/premiseService";
import { showApiError } from "../../services/apiClient";
import { pick, pickId, formatDate } from "../../utils/data";

export default function RentRequestPage() {
  const { role } = useAuth();
  const isTenant = role === ROLE.KHACH_THUE;
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();
  
  const [vacantPremises, setVacantPremises] = useState([]);

  const fetcher = useCallback(
    (p) => (isTenant ? rentRequestService.myRequests(p) : rentRequestService.list(p)),
    [isTenant]
  );
  const { items, loading, reload } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  // Load vacant premises when opening the request modal
  useEffect(() => {
    if (isTenant && open) {
      const loadVacant = async () => {
        try {
          const res = await premiseService.list({ page: 1, page_size: 100 });
          const list = res?.items || res || [];
          setVacantPremises(list);
        } catch (e) {
          console.error("Lỗi khi tải danh sách mặt bằng trống:", e);
        }
      };
      loadVacant();
    }
  }, [isTenant, open]);

  const create = async () => {
    try {
      await rentRequestService.create(form.getFieldsValue(true));
      message.success("Đã gửi yêu cầu thuê thêm");
      setOpen(false);
      form.resetFields();
      reload();
    } catch (e) {
      showApiError(e);
    }
  };

  const review = async (row, ket_qua) => {
    try {
      const payload = { ket_qua };
      if (ket_qua === "TU_CHOI") {
        payload.ly_do_tu_choi = "Không đáp ứng điều kiện thuê thêm";
      } else {
        payload.ghi_chu_cho_kdtc = "Chuyển sang số hóa hợp đồng";
      }
      await rentRequestService.review(
        pickId(row, ["ma_yeu_cau", "ma_yc", "MAYC"]),
        payload
      );
      message.success("Đã xử lý yêu cầu");
      reload();
    } catch (e) {
      showApiError(e);
    }
  };

  const columns = [
    {
      title: "Mã YC",
      render: (_, r) => pick(r, ["ma_yeu_cau", "ma_yc", "MAYC"]),
    },
    {
      title: "Khách thuê",
      render: (_, r) => pick(r, ["ma_khach_thue", "ma_kh", "MAKH"]),
    },
    {
      title: "Mặt bằng",
      render: (_, r) => pick(r, ["ma_mat_bang", "ma_mb", "MAMB"]),
    },
    {
      title: "Ngày gửi",
      render: (_, r) => formatDate(pick(r, ["ngay_gui", "NGAYGUI"])),
    },
    {
      title: "Lý do",
      render: (_, r) => pick(r, ["ly_do", "LYDO"]),
    },
    {
      title: "Trạng thái",
      render: (_, r) => <StatusTag value={pick(r, ["trang_thai", "TRANGTHAI"])} />,
    },
    {
      title: "Thao tác",
      align: "right",
      render: (_, r) =>
        !isTenant ? (
          <Space>
            <Button icon={<CheckOutlined />} onClick={() => review(r, "DUYET")}>
              Duyệt
            </Button>
            <Button danger icon={<CloseOutlined />} onClick={() => review(r, "TU_CHOI")}>
              Từ chối
            </Button>
          </Space>
        ) : null,
    },
  ];

  return (
    <>
      <PageHeader
        title={isTenant ? "Yêu cầu thuê thêm" : "Duyệt yêu cầu thuê thêm"}
        breadcrumb={["Hợp đồng", "Yêu cầu thuê thêm"]}
        actionText={isTenant ? "Gửi yêu cầu" : null}
        actionIcon={<PlusOutlined />}
        onAction={() => setOpen(true)}
      />
      <ResponsiveTable
        rowKey={(r) => pickId(r, ["ma_yeu_cau", "ma_yc", "MAYC"])}
        columns={columns}
        dataSource={items}
        loading={loading}
      />
      
      <Modal
        title="Gửi yêu cầu thuê thêm"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={create}
        okText="Gửi yêu cầu"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="ma_mat_bang"
            label="Mặt bằng muốn thuê thêm"
            rules={[{ required: true, message: "Vui lòng chọn mặt bằng muốn thuê thêm" }]}
          >
            <Select
              placeholder="Chọn mặt bằng còn trống"
              showSearch
              optionFilterProp="children"
              options={vacantPremises.map((item) => {
                const ma = pick(item, ["ma_mat_bang", "ma_mb", "MAMB"]);
                const viTri = pick(item, ["vi_tri", "VITRI"]);
                const dienTich = pick(item, ["dien_tich", "DIENTICH"]);
                return {
                  value: ma,
                  label: `${ma} - ${viTri} (${dienTich} m²)`,
                };
              })}
            />
          </Form.Item>
          <Form.Item
            name="ly_do"
            label="Lý do"
            rules={[{ required: true, message: "Vui lòng nhập lý do" }]}
          >
            <Input.TextArea rows={4} placeholder="Nhập lý do thuê thêm..." />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
