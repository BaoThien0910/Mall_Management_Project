import { PlusOutlined, FilterOutlined } from "@ant-design/icons";
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
  Popover,
  DatePicker,
} from "antd";
import { useCallback, useState, useRef, useEffect } from "react";
import dayjs from "dayjs";

import PageHeader from "../../components/common/PageHeader";
import ResponsiveTable from "../../components/common/ResponsiveTable";
import StatusTag from "../../components/common/StatusTag";
import Toolbar from "../../components/common/Toolbar";
import { DOI_TUONG_NHAN, LOAI_THONG_BAO } from "../../constants/statuses";
import { ROLE } from "../../constants/roles";
import { useAuth } from "../../hooks/useAuth";
import { notificationService } from "../../services/notificationService";
import { showApiError } from "../../services/apiClient";
import { useCrudList } from "../../hooks/useCrudList";
import { formatDate, pick, pickId } from "../../utils/data";

const { Title, Paragraph, Text } = Typography;

const THONG_BAO_STATUS = ["Đã ban hành", "Đã thu hồi"];

export default function NotificationListPage() {
  const { role } = useAuth();
  const canCreate = role === ROLE.BQL;
  const [open, setOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selected, setSelected] = useState(null);
  const [form] = Form.useForm();

  const [keyword, setKeyword] = useState("");
  const [popoverOpen, setPopoverOpen] = useState(false);
  const timerRef = useRef(null);

  const [appliedFilters, setAppliedFilters] = useState({
    loai_thong_bao: undefined,
    doi_tuong_nhan: undefined,
    ngay_tu: undefined,
    ngay_den: undefined,
    trang_thai: undefined,
  });

  const [tempLoaiThongBao, setTempLoaiThongBao] = useState(undefined);
  const [tempDoiTuongNhan, setTempDoiTuongNhan] = useState(undefined);
  const [tempNgayTu, setTempNgayTu] = useState("");
  const [tempNgayDen, setTempNgayDen] = useState("");
  const [tempTrangThai, setTempTrangThai] = useState(undefined);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  const fetcher = useCallback((params) => notificationService.list(params), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, {
    page: 1,
    page_size: 20,
  });

  const applySearch = (val) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    timerRef.current = setTimeout(() => {
      const activeFilters = {};
      Object.keys(appliedFilters).forEach((key) => {
        if (appliedFilters[key] !== undefined && appliedFilters[key] !== null && appliedFilters[key] !== "") {
          activeFilters[key] = appliedFilters[key];
        }
      });
      setParams({
        keyword: val || undefined,
        ...activeFilters,
        page: 1,
        page_size: 20,
      });
    }, 500);
  };

  const handleApply = () => {
    const nextFilters = {
      loai_thong_bao: tempLoaiThongBao || undefined,
      doi_tuong_nhan: tempDoiTuongNhan || undefined,
      ngay_tu: tempNgayTu || undefined,
      ngay_den: tempNgayDen || undefined,
      trang_thai: tempTrangThai || undefined,
    };
    setAppliedFilters(nextFilters);

    const cleanFilters = {};
    Object.keys(nextFilters).forEach((key) => {
      if (nextFilters[key] !== undefined && nextFilters[key] !== null && nextFilters[key] !== "") {
        cleanFilters[key] = nextFilters[key];
      }
    });

    setParams({
      keyword: keyword || undefined,
      ...cleanFilters,
      page: 1,
      page_size: 20,
    });
    setPopoverOpen(false);
  };

  const handleCancel = () => {
    setTempLoaiThongBao(appliedFilters.loai_thong_bao);
    setTempDoiTuongNhan(appliedFilters.doi_tuong_nhan);
    setTempNgayTu(appliedFilters.ngay_tu || "");
    setTempNgayDen(appliedFilters.ngay_den || "");
    setTempTrangThai(appliedFilters.trang_thai);
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempLoaiThongBao(undefined);
    setTempDoiTuongNhan(undefined);
    setTempNgayTu("");
    setTempNgayDen("");
    setTempTrangThai(undefined);

    setAppliedFilters({
      loai_thong_bao: undefined,
      doi_tuong_nhan: undefined,
      ngay_tu: undefined,
      ngay_den: undefined,
      trang_thai: undefined,
    });
    setPopoverOpen(false);

    setParams({
      keyword: keyword || undefined,
      page: 1,
      page_size: 20,
    });
  };

  const handleReload = () => {
    setKeyword("");
    setAppliedFilters({
      loai_thong_bao: undefined,
      doi_tuong_nhan: undefined,
      ngay_tu: undefined,
      ngay_den: undefined,
      trang_thai: undefined,
    });
    setTempLoaiThongBao(undefined);
    setTempDoiTuongNhan(undefined);
    setTempNgayTu("");
    setTempNgayDen("");
    setTempTrangThai(undefined);
    setParams({
      page: 1,
      page_size: 20,
    });
    reload();
  };

  const activeFiltersCount =
    (appliedFilters.loai_thong_bao ? 1 : 0) +
    (appliedFilters.doi_tuong_nhan ? 1 : 0) +
    (appliedFilters.ngay_tu ? 1 : 0) +
    (appliedFilters.ngay_den ? 1 : 0) +
    (appliedFilters.trang_thai ? 1 : 0);

  const filterContent = (
    <div style={{ padding: "8px", width: 340 }}>
      <div style={{ marginBottom: "12px" }}>
        <div style={{ fontWeight: 600, marginBottom: "6px" }}>Loại thông báo</div>
        <Select
          placeholder="Chọn loại"
          value={tempLoaiThongBao}
          onChange={setTempLoaiThongBao}
          style={{ width: "100%" }}
          allowClear
          options={LOAI_THONG_BAO.map((item) => ({ value: item, label: item }))}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <div style={{ fontWeight: 600, marginBottom: "6px" }}>Đối tượng nhận</div>
        <Select
          placeholder="Chọn đối tượng"
          value={tempDoiTuongNhan}
          onChange={setTempDoiTuongNhan}
          style={{ width: "100%" }}
          allowClear
          options={DOI_TUONG_NHAN.map((item) => ({ value: item, label: item }))}
        />
      </div>

      <div style={{ marginBottom: "12px" }}>
        <div style={{ fontWeight: 600, marginBottom: "6px" }}>Ngày ban hành</div>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ color: "#555", width: "40px" }}>Từ:</span>
            <DatePicker
              value={tempNgayTu ? dayjs(tempNgayTu) : null}
              onChange={(date) => setTempNgayTu(date ? dayjs(date).format("YYYY-MM-DD") : "")}
              format="DD/MM/YYYY"
              placeholder="Từ ngày"
              style={{ width: "100%" }}
              allowClear={false}
            />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ color: "#555", width: "40px" }}>Đến:</span>
            <DatePicker
              value={tempNgayDen ? dayjs(tempNgayDen) : null}
              onChange={(date) => setTempNgayDen(date ? dayjs(date).format("YYYY-MM-DD") : "")}
              format="DD/MM/YYYY"
              placeholder="Đến ngày"
              style={{ width: "100%" }}
              allowClear={false}
            />
          </div>
        </div>
      </div>

      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontWeight: 600, marginBottom: "6px" }}>Trạng thái</div>
        <Select
          placeholder="Chọn trạng thái"
          value={tempTrangThai}
          onChange={setTempTrangThai}
          style={{ width: "100%" }}
          allowClear
          options={THONG_BAO_STATUS.map((item) => ({ value: item, label: item }))}
        />
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Button type="primary" danger onClick={handleClearFilters}>
          Xóa bộ lọc
        </Button>
        <Space>
          <Button onClick={handleCancel}>Hủy</Button>
          <Button type="primary" onClick={handleApply}>
            Áp dụng
          </Button>
        </Space>
      </div>
    </div>
  );

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

  const revoke = (row) => {
    Modal.confirm({
      title: "Xác nhận thu hồi thông báo",
      content: "Bạn có chắc chắn muốn thu hồi thông báo này không? Các tài khoản khác sẽ không thể nhìn thấy thông báo này nữa.",
      okText: "Xác nhận",
      cancelText: "Hủy",
      okButtonProps: { danger: true },
      onOk: async () => {
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
      },
    });
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
      align: "left",
      render: (_, record) => {
        const trangThai = pick(record, ["trang_thai", "TRANGTHAI"]);
        const canView = trangThai !== "Đã thu hồi" || role === ROLE.BQL || role === ROLE.QTV;
        return (
          <Space>
            {canView ? (
              <Button type="link" onClick={() => viewDetail(record)}>
                Xem nội dung
              </Button>
            ) : null}
            {canCreate && trangThai === "Đã ban hành" ? (
              <Button danger type="link" onClick={() => revoke(record)}>
                Thu hồi
              </Button>
            ) : null}
          </Space>
        );
      },
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

      <Toolbar
        keyword={keyword}
        onKeywordChange={(val) => {
          setKeyword(val);
          applySearch(val);
        }}
        placeholder="Tìm kiếm"
        onReload={handleReload}
      >
        <Popover
          content={filterContent}
          trigger="click"
          open={popoverOpen}
          onOpenChange={(visible) => {
            setPopoverOpen(visible);
            if (!visible) {
              handleCancel();
            }
          }}
          placement="bottomLeft"
          overlayStyle={{ zIndex: 1050 }}
        >
          <Button
            type="primary"
            icon={<FilterOutlined />}
            style={{
              minWidth: 100,
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span style={{ display: "inline-flex", alignItems: "center" }}>Lọc</span>
            {activeFiltersCount > 0 && (
              <span
                style={{
                  marginLeft: 8,
                  backgroundColor: "#fff",
                  color: "#1677ff",
                  borderRadius: "50%",
                  width: "20px",
                  height: "20px",
                  fontSize: "12px",
                  fontWeight: 600,
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  lineHeight: "1",
                }}
              >
                {activeFiltersCount}
              </span>
            )}
          </Button>
        </Popover>
      </Toolbar>

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
