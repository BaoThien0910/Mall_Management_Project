import { EditOutlined, PlusOutlined, StopOutlined } from "@ant-design/icons";
import { Button, Form, Input, Modal, Popconfirm, Select, Space, message } from "antd";
import { useCallback, useState } from "react";
import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import Toolbar from "../../components/common/Toolbar";
import { ROLE, ROLE_LABEL } from "../../constants/roles";
import { accountService } from "../../services/accountService";
import { showApiError } from "../../services/apiClient";
import { pick, pickId } from "../../utils/data";
import { useCrudList } from "../../hooks/useCrudList";

export default function AccountListPage() {
  const fetcher = useCallback((params) => accountService.list(params), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, { page: 1, page_size: 20 });
  const [keyword, setKeyword] = useState("");
  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const create = async () => {
    try {
      await accountService.create(form.getFieldsValue(true));
      message.success("Tạo tài khoản thành công");
      setOpen(false);
      form.resetFields();
      reload();
    } catch (error) { showApiError(error); }
  };

  const disable = async (row) => {
    try {
      const id = pickId(row, ["ma_tai_khoan", "ma_tk", "MATK"]);
      await accountService.disable(id, { ly_do: "Vô hiệu hóa từ giao diện quản trị" });
      message.success("Đã vô hiệu hóa tài khoản");
      reload();
    } catch (error) { showApiError(error); }
  };

  const columns = [
    { title: "Tên người dùng", render: (_, r) => pick(r, ["ten_dang_nhap", "username", "TENDANGNHAP"]) },
    { title: "Mã tài khoản", render: (_, r) => pick(r, ["ma_tai_khoan", "ma_tk", "MATK"]) },
    { title: "Vai trò", render: (_, r) => <StatusTag value={ROLE_LABEL[pick(r, ["ma_vai_tro", "MAVAITRO"])] || pick(r, ["ma_vai_tro", "MAVAITRO"])} /> },
    { title: "Trạng thái", render: (_, r) => <StatusTag value={pick(r, ["trang_thai", "TRANGTHAI"])} /> },
    { title: "Thao tác", align: "right", render: (_, r) => <Space><Button type="text" icon={<EditOutlined />} /><Popconfirm title="Vô hiệu hóa tài khoản này?" onConfirm={() => disable(r)}><Button danger type="text" icon={<StopOutlined />} /></Popconfirm></Space> },
  ];

  return <>
    <PageHeader title="Quản lý Tài khoản" breadcrumb={["Quản trị", "Tài khoản"]} actionText="Thêm tài khoản" actionIcon={<PlusOutlined />} onAction={() => setOpen(true)} />
    <Toolbar keyword={keyword} onKeywordChange={setKeyword} onSearch={() => setParams({ keyword, page: 1, page_size: 20 })} onReload={reload} />
    <ResponsiveTable rowKey={(r) => pickId(r, ["ma_tai_khoan", "ma_tk", "MATK"])} columns={columns} dataSource={items} loading={loading} />
    <Modal title="Thêm tài khoản" open={open} onCancel={() => setOpen(false)} onOk={create} okText="Tạo tài khoản">
      <Form form={form} layout="vertical">
        <Form.Item name="ten_dang_nhap" label="Tên đăng nhập" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="mat_khau_tam" label="Mật khẩu tạm" rules={[{ required: true }]}><Input.Password /></Form.Item>
        <Form.Item name="ma_vai_tro" label="Vai trò" rules={[{ required: true }]}><Select options={Object.values(ROLE).map((v) => ({ value: v, label: ROLE_LABEL[v] }))} /></Form.Item>
        <Form.Item name="ma_nhan_vien" label="Mã nhân viên"><Input placeholder="Bỏ trống nếu là khách thuê" /></Form.Item>
        <Form.Item name="ma_khach_thue" label="Mã khách thuê"><Input placeholder="Bỏ trống nếu là nhân viên" /></Form.Item>
      </Form>
    </Modal>
  </>;
}
