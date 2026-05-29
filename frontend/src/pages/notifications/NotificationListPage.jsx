import { FilterOutlined, PlusOutlined, ReloadOutlined, SearchOutlined } from "@ant-design/icons";
import {
  Button,
  Card,
  Checkbox,
  Col,
  DatePicker,
  Divider,
  Drawer,
  Form,
  Input,
  Modal,
  Popover,
  Row,
  Select,
  Space,
  Typography,
  message,
} from "antd";
import { useCallback, useEffect, useRef, useState } from "react";
import dayjs from "dayjs";

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

  // Search keyword state
  const [keyword, setKeyword] = useState("");

  // Popover open state
  const [popoverOpen, setPopoverOpen] = useState(false);

  // Filter States
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [selectedRecipients, setSelectedRecipients] = useState([]);
  const [selectedStatuses, setSelectedStatuses] = useState([]);
  const [tuNgay, setTuNgay] = useState("");
  const [denNgay, setDenNgay] = useState("");

  // Temp Filter States (in popover)
  const [tempTypes, setTempTypes] = useState([]);
  const [tempRecipients, setTempRecipients] = useState([]);
  const [tempStatuses, setTempStatuses] = useState([]);
  const [tempTuNgay, setTempTuNgay] = useState("");
  const [tempDenNgay, setTempDenNgay] = useState("");

  const timerRef = useRef(null);

  // Clean up timer on unmount
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

  const applyFilters = (updates, immediate = false) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    const run = () => {
      const nextFilters = {
        keyword: keyword || undefined,
        loai_thong_bao: selectedTypes.length ? selectedTypes.join(",") : undefined,
        doi_tuong_nhan: selectedRecipients.length ? selectedRecipients.join(",") : undefined,
        trang_thai: selectedStatuses.length ? selectedStatuses.join(",") : undefined,
        tu_ngay: tuNgay ? `${tuNgay}T00:00:00` : undefined,
        den_ngay: denNgay ? `${denNgay}T23:59:59` : undefined,
        ...updates
      };

      const cleanParams = {};
      Object.keys(nextFilters).forEach(key => {
        if (nextFilters[key] !== undefined && nextFilters[key] !== null && nextFilters[key] !== "") {
          cleanParams[key] = nextFilters[key];
        }
      });

      setParams({
        ...cleanParams,
        page: 1,
        page_size: 20,
      });
    };

    if (immediate) {
      run();
    } else {
      timerRef.current = setTimeout(run, 500);
    }
  };

  const handleKeywordSearch = () => {
    applyFilters({ keyword: keyword || undefined }, true);
  };

  const handleOpenPopover = (visible) => {
    if (visible) {
      setTempTypes(selectedTypes);
      setTempRecipients(selectedRecipients);
      setTempStatuses(selectedStatuses);
      setTempTuNgay(tuNgay);
      setTempDenNgay(denNgay);
    }
    setPopoverOpen(visible);
  };

  const handleApply = () => {
    setSelectedTypes(tempTypes);
    setSelectedRecipients(tempRecipients);
    setSelectedStatuses(tempStatuses);
    setTuNgay(tempTuNgay);
    setDenNgay(tempDenNgay);
    setPopoverOpen(false);

    applyFilters({
      loai_thong_bao: tempTypes.length ? tempTypes.join(",") : undefined,
      doi_tuong_nhan: tempRecipients.length ? tempRecipients.join(",") : undefined,
      trang_thai: tempStatuses.length ? tempStatuses.join(",") : undefined,
      tu_ngay: tempTuNgay ? `${tempTuNgay}T00:00:00` : undefined,
      den_ngay: tempDenNgay ? `${tempDenNgay}T23:59:59` : undefined,
    }, true);
  };

  const handleCancel = () => {
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempTypes([]);
    setTempRecipients([]);
    setTempStatuses([]);
    setTempTuNgay("");
    setTempDenNgay("");

    setSelectedTypes([]);
    setSelectedRecipients([]);
    setSelectedStatuses([]);
    setTuNgay("");
    setDenNgay("");
    setPopoverOpen(false);

    applyFilters({
      loai_thong_bao: undefined,
      doi_tuong_nhan: undefined,
      trang_thai: undefined,
      tu_ngay: undefined,
      den_ngay: undefined,
    }, true);
  };

  const handleClearAll = () => {
    setKeyword("");
    setSelectedTypes([]);
    setSelectedRecipients([]);
    setSelectedStatuses([]);
    setTuNgay("");
    setDenNgay("");
    setTempTypes([]);
    setTempRecipients([]);
    setTempStatuses([]);
    setTempTuNgay("");
    setTempDenNgay("");

    applyFilters({
      keyword: undefined,
      loai_thong_bao: undefined,
      doi_tuong_nhan: undefined,
      trang_thai: undefined,
      tu_ngay: undefined,
      den_ngay: undefined
    }, true);
  };

  const handleReload = () => {
    reload();
  };

  const handleRemoveType = (item) => {
    const next = selectedTypes.filter(t => t !== item);
    setSelectedTypes(next);
    applyFilters({ loai_thong_bao: next.length ? next.join(",") : undefined }, true);
  };

  const handleRemoveRecipient = (item) => {
    const next = selectedRecipients.filter(r => r !== item);
    setSelectedRecipients(next);
    applyFilters({ doi_tuong_nhan: next.length ? next.join(",") : undefined }, true);
  };

  const handleRemoveStatus = (item) => {
    const next = selectedStatuses.filter(s => s !== item);
    setSelectedStatuses(next);
    applyFilters({ trang_thai: next.length ? next.join(",") : undefined }, true);
  };

  const handleRemoveDate = () => {
    setTuNgay("");
    setDenNgay("");
    applyFilters({ tu_ngay: undefined, den_ngay: undefined }, true);
  };

  const activeFiltersCount = selectedTypes.length + selectedRecipients.length + selectedStatuses.length + (tuNgay || denNgay ? 1 : 0);
  const hasActiveFilters = activeFiltersCount > 0 || keyword !== "";

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

  const renderFilterTag = (label, onRemove) => {
    return (
      <div
        key={label}
        style={{
          backgroundColor: '#e6f4ff',
          color: '#1677ff',
          border: '1px solid #91caff',
          borderRadius: '6px',
          fontSize: '13px',
          padding: '4px 12px',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          fontWeight: 500,
          lineHeight: '1.4',
          userSelect: 'none'
        }}
      >
        <span>{label}</span>
        <span
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          style={{
            cursor: 'pointer',
            fontSize: '12px',
            color: '#1677ff',
            display: 'inline-flex',
            alignItems: 'center',
            opacity: 0.85,
            transition: 'opacity 0.2s',
            fontWeight: 'bold'
          }}
          onMouseEnter={(e) => e.target.style.opacity = 1}
          onMouseLeave={(e) => e.target.style.opacity = 0.85}
        >
          ✕
        </span>
      </div>
    );
  };

  const renderActiveTags = () => {
    if (!hasActiveFilters) return null;
    return (
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center', marginTop: '12px' }}>
        {selectedTypes.map(t => renderFilterTag(t, () => handleRemoveType(t)))}
        {selectedRecipients.map(r => renderFilterTag(r, () => handleRemoveRecipient(r)))}
        {selectedStatuses.map(s => renderFilterTag(s, () => handleRemoveStatus(s)))}
        {(tuNgay || denNgay) && renderFilterTag(
          `Ngày ban hành: ${tuNgay ? dayjs(tuNgay).format("DD/MM/YYYY") : "..."} - ${denNgay ? dayjs(denNgay).format("DD/MM/YYYY") : "..."}`,
          handleRemoveDate
        )}
        
        <span
          onClick={handleClearAll}
          style={{
            color: '#1677ff',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: 500,
            marginLeft: '4px',
            userSelect: 'none'
          }}
          onMouseEnter={(e) => e.target.style.textDecoration = 'underline'}
          onMouseLeave={(e) => e.target.style.textDecoration = 'none'}
        >
          Xóa tất cả
        </span>
      </div>
    );
  };

  const filterContent = (
    <div style={{ padding: '4px', width: 480 }}>
      <Row gutter={16}>
        {/* Cột 1: Loại */}
        <Col span={8}>
          <div style={{ fontWeight: 600, marginBottom: 12, fontSize: '13px', color: '#111' }}>Loại</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {LOAI_THONG_BAO.map(type => {
              const checked = tempTypes.includes(type);
              return (
                <Checkbox
                  key={type}
                  checked={checked}
                  onChange={(e) => {
                    const next = e.target.checked
                      ? [...tempTypes, type]
                      : tempTypes.filter(t => t !== type);
                    setTempTypes(next);
                  }}
                >
                  {type}
                </Checkbox>
              );
            })}
          </div>
        </Col>

        {/* Cột 2: Đối tượng nhận */}
        <Col span={8}>
          <div style={{ fontWeight: 600, marginBottom: 12, fontSize: '13px', color: '#111' }}>Đối tượng nhận</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {DOI_TUONG_NHAN.map(r => {
              const checked = tempRecipients.includes(r);
              return (
                <Checkbox
                  key={r}
                  checked={checked}
                  onChange={(e) => {
                    const next = e.target.checked
                      ? [...tempRecipients, r]
                      : tempRecipients.filter(item => item !== r);
                    setTempRecipients(next);
                  }}
                >
                  {r}
                </Checkbox>
              );
            })}
          </div>
        </Col>

        {/* Cột 3: Trạng thái */}
        <Col span={8}>
          <div style={{ fontWeight: 600, marginBottom: 12, fontSize: '13px', color: '#111' }}>Trạng thái</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {["Đã ban hành", "Đã thu hồi"].map(status => {
              const checked = tempStatuses.includes(status);
              return (
                <Checkbox
                  key={status}
                  checked={checked}
                  onChange={(e) => {
                    const next = e.target.checked
                      ? [...tempStatuses, status]
                      : tempStatuses.filter(s => s !== status);
                    setTempStatuses(next);
                  }}
                >
                  {status}
                </Checkbox>
              );
            })}
          </div>
        </Col>
      </Row>
      
      <Divider style={{ margin: '12px 0' }} />
      
      <div>
        <div style={{ fontWeight: 600, marginBottom: 8, fontSize: '13px', color: '#111' }}>Ngày ban hành</div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <DatePicker
            value={tempTuNgay ? dayjs(tempTuNgay) : null}
            onChange={(date) => setTempTuNgay(date ? dayjs(date).format("YYYY-MM-DD") : "")}
            format="DD/MM/YYYY"
            placeholder="Từ ngày"
            style={{ width: "100%" }}
            allowClear={false}
          />
          <span style={{ color: "#bfbfbf" }}>-</span>
          <DatePicker
            value={tempDenNgay ? dayjs(tempDenNgay) : null}
            onChange={(date) => setTempDenNgay(date ? dayjs(date).format("YYYY-MM-DD") : "")}
            format="DD/MM/YYYY"
            placeholder="Đến ngày"
            style={{ width: "100%" }}
            allowClear={false}
          />
        </div>
      </div>
      
      <Divider style={{ margin: '12px 0' }} />
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button type="primary" danger onClick={handleClearFilters}>Xóa bộ lọc</Button>
        <Space>
          <Button onClick={handleCancel}>Hủy</Button>
          <Button type="primary" onClick={handleApply}>
            Áp dụng
          </Button>
        </Space>
      </div>
    </div>
  );

  return (
    <>
      <PageHeader
        title="Thông báo"
        breadcrumb={["Thông báo"]}
        actionText={canCreate ? "Ban hành" : undefined}
        actionIcon={canCreate ? <PlusOutlined /> : undefined}
        onAction={canCreate ? () => setOpen(true) : undefined}
      />

      <Card className="toolbar-card" bordered={false} style={{ marginBottom: '16px' }} styles={{ body: { padding: '16px' } }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Input
            allowClear
            prefix={<SearchOutlined />}
            placeholder="Tìm kiếm Tiêu đề"
            value={keyword}
            onChange={(e) => {
              const val = e.target.value;
              setKeyword(val);
              applyFilters({ keyword: val || undefined }, !val);
            }}
            onPressEnter={handleKeywordSearch}
            style={{ width: 340 }}
          />
          
          <Popover
            content={filterContent}
            title="Bộ lọc"
            trigger="click"
            open={popoverOpen}
            onOpenChange={handleOpenPopover}
            placement="bottomLeft"
            overlayStyle={{ zIndex: 1050 }}
          >
            <Button
              type="primary"
              icon={<FilterOutlined />}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                height: '38px',
                borderRadius: '8px',
              }}
            >
              <span style={{ display: 'inline-flex', alignItems: 'center' }}>Lọc</span>
              {activeFiltersCount > 0 && (
                <span
                  style={{
                    marginLeft: 8,
                    backgroundColor: '#fff',
                    color: '#1677ff',
                    borderRadius: '50%',
                    width: '20px',
                    height: '20px',
                    fontSize: '12px',
                    fontWeight: 600,
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    lineHeight: '1',
                  }}
                >
                  {activeFiltersCount}
                </span>
              )}
            </Button>
          </Popover>
          
          <Button icon={<ReloadOutlined />} onClick={handleReload}>
            Tải lại
          </Button>
        </div>
        {renderActiveTags()}
      </Card>

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
