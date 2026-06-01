import {
  DeleteOutlined,
  FilterOutlined,
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
  Popover,
  Checkbox,
  Row,
  Col,
  Card,
  Divider,
} from "antd";
import { useCallback, useState, useEffect, useRef } from "react";

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
  const isTenant = role === ROLE.KHACH_THUE;

  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  // Dynamic filter options extracted from existing premises
  const [allFloors, setAllFloors] = useState([]);
  const [allTypes, setAllTypes] = useState([]);

  // Search keyword state
  const [keyword, setKeyword] = useState("");

  // Popover open state
  const [popoverOpen, setPopoverOpen] = useState(false);

  const timerRef = useRef(null);

  // Clean up timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  // Unified Filter States
  const [selectedStatuses, setSelectedStatuses] = useState([]);
  const [selectedFloors, setSelectedFloors] = useState([]);
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [minArea, setMinArea] = useState(null);
  const [maxArea, setMaxArea] = useState(null);

  // Temporary Filter States for Popover
  const [tempStatuses, setTempStatuses] = useState([]);
  const [tempFloors, setTempFloors] = useState([]);
  const [tempTypes, setTempTypes] = useState([]);
  const [tempMinArea, setTempMinArea] = useState(null);
  const [tempMaxArea, setTempMaxArea] = useState(null);

  // Fetch unique floors & types on mount
  const loadFilterOptions = useCallback(async () => {
    try {
      const res = await premiseService.list({ page: 1, page_size: 100 });
      const items = res?.items || res || [];

      // Trích xuất các tầng duy nhất
      const floors = Array.from(new Set(items.map(item => pick(item, ["tang", "TANG"]))))
        .filter(f => f !== undefined && f !== null)
        .sort((a, b) => a - b);

      // Trích xuất các loại mặt bằng duy nhất
      const types = Array.from(new Set(items.map(item => pick(item, ["loai_mat_bang", "loai_mb", "LOAIMB"]))))
        .filter(t => !!t)
        .sort();

      setAllFloors(floors);
      setAllTypes(types);
    } catch (e) {
      console.error("Lỗi khi tải danh sách bộ lọc động:", e);
    }
  }, []);

  useEffect(() => {
    loadFilterOptions();
  }, [loadFilterOptions]);

  const fetcher = useCallback((p) => premiseService.list(p), []);
  const { items, loading, reload, setParams } = useCrudList(fetcher, { page: 1, page_size: 20 });

  const create = async () => {
    try {
      const values = await form.validateFields();
      await premiseService.create(values);
      message.success("Tạo mặt bằng thành công");
      setOpen(false);
      form.resetFields();
      reload();
      loadFilterOptions();
    } catch (error) {
      showApiError(error);
    }
  };

  const remove = async (record) => {
    try {
      await premiseService.remove(getPremiseId(record));
      message.success("Đã xóa mặt bằng");
      reload();
      loadFilterOptions();
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

  const applyFilters = (updates, immediate = false) => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    const run = () => {
      const nextFilters = {
        keyword: keyword || undefined,
        trang_thai: selectedStatuses.length ? selectedStatuses.join(",") : undefined,
        tang: selectedFloors.length ? selectedFloors.join(",") : undefined,
        loai_mat_bang: selectedTypes.length ? selectedTypes.join(",") : undefined,
        dien_tich_tu: minArea !== null && minArea !== "" ? minArea : undefined,
        dien_tich_den: maxArea !== null && maxArea !== "" ? maxArea : undefined,
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
      setTempStatuses(selectedStatuses);
      setTempFloors(selectedFloors);
      setTempTypes(selectedTypes);
      setTempMinArea(minArea);
      setTempMaxArea(maxArea);
    }
    setPopoverOpen(visible);
  };

  const handleApply = () => {
    setSelectedStatuses(tempStatuses);
    setSelectedFloors(tempFloors);
    setSelectedTypes(tempTypes);
    setMinArea(tempMinArea);
    setMaxArea(tempMaxArea);
    setPopoverOpen(false);

    applyFilters({
      trang_thai: tempStatuses.length ? tempStatuses.join(",") : undefined,
      tang: tempFloors.length ? tempFloors.join(",") : undefined,
      loai_mat_bang: tempTypes.length ? tempTypes.join(",") : undefined,
      dien_tich_tu: tempMinArea !== null && tempMinArea !== "" ? tempMinArea : undefined,
      dien_tich_den: tempMaxArea !== null && tempMaxArea !== "" ? tempMaxArea : undefined,
    }, true);
  };

  const handleCancel = () => {
    setPopoverOpen(false);
  };

  const handleClearFilters = () => {
    setTempStatuses([]);
    setTempFloors([]);
    setTempTypes([]);
    setTempMinArea(null);
    setTempMaxArea(null);

    setSelectedStatuses([]);
    setSelectedFloors([]);
    setSelectedTypes([]);
    setMinArea(null);
    setMaxArea(null);
    setPopoverOpen(false);

    applyFilters({
      trang_thai: undefined,
      tang: undefined,
      loai_mat_bang: undefined,
      dien_tich_tu: undefined,
      dien_tich_den: undefined,
    }, true);
  };

  const handleClearAll = () => {
    setKeyword("");
    setSelectedStatuses([]);
    setSelectedFloors([]);
    setSelectedTypes([]);
    setMinArea(null);
    setMaxArea(null);

    applyFilters({
      keyword: undefined,
      trang_thai: undefined,
      tang: undefined,
      loai_mat_bang: undefined,
      dien_tich_tu: undefined,
      dien_tich_den: undefined
    }, true);
  };

  const handleRemoveStatus = (statusToRemove) => {
    const next = selectedStatuses.filter(s => s !== statusToRemove);
    setSelectedStatuses(next);
    applyFilters({ trang_thai: next.length ? next.join(",") : undefined }, true);
  };

  const handleRemoveFloor = (floorToRemove) => {
    const next = selectedFloors.filter(f => f !== floorToRemove);
    setSelectedFloors(next);
    applyFilters({ tang: next.length ? next.join(",") : undefined }, true);
  };

  const handleRemoveType = (typeToRemove) => {
    const next = selectedTypes.filter(t => t !== typeToRemove);
    setSelectedTypes(next);
    applyFilters({ loai_mat_bang: next.length ? next.join(",") : undefined }, true);
  };

  const handleRemoveMinArea = () => {
    setMinArea(null);
    applyFilters({ dien_tich_tu: undefined }, true);
  };

  const handleRemoveMaxArea = () => {
    setMaxArea(null);
    applyFilters({ dien_tich_den: undefined }, true);
  };

  const handleReload = () => {
    setKeyword("");
    setTempStatuses([]);
    setTempFloors([]);
    setTempTypes([]);
    setTempMinArea(null);
    setTempMaxArea(null);

    setSelectedStatuses([]);
    setSelectedFloors([]);
    setSelectedTypes([]);
    setMinArea(null);
    setMaxArea(null);

    setParams({
      page: 1,
      page_size: 20,
    });
    reload();
    loadFilterOptions();
  };

  const activeFiltersCount = selectedStatuses.length + selectedFloors.length + selectedTypes.length + 
    (minArea !== null && minArea !== "" ? 1 : 0) + 
    (maxArea !== null && maxArea !== "" ? 1 : 0);

  const hasActiveFilters = activeFiltersCount > 0 || keyword !== "";

  const filterContent = (
    <div style={{ padding: '4px', width: 480 }}>
      <Row gutter={16}>
        {/* Cột 1: Trạng thái */}
        <Col span={8}>
          <div style={{ fontWeight: 600, marginBottom: 12, fontSize: '13px', color: '#111' }}>
            Trạng thái{isTenant ? " (Cố định)" : ""}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {MAT_BANG_STATUS.map(status => {
              const checked = isTenant ? status === "Còn trống" : tempStatuses.includes(status);
              return (
                <Checkbox
                  key={status}
                  checked={checked}
                  disabled={isTenant}
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

        {/* Cột 2: Tầng */}
        <Col span={8}>
          <div style={{ fontWeight: 600, marginBottom: 12, fontSize: '13px', color: '#111' }}>Tầng</div>
          <div style={{ maxHeight: '130px', overflowY: 'auto', paddingRight: '4px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {allFloors.map(floor => {
              const checked = tempFloors.includes(floor);
              const label = floor === 0 ? "Tầng trệt" : `Tầng ${floor}`;
              return (
                <div
                  key={floor}
                  style={{
                    border: `1px solid ${checked ? '#1677ff' : 'transparent'}`,
                    backgroundColor: checked ? '#e6f4ff' : 'transparent',
                    borderRadius: '6px',
                    padding: '4px 8px',
                    display: 'flex',
                    alignItems: 'center',
                    transition: 'all 0.2s',
                  }}
                >
                  <Checkbox
                    checked={checked}
                    onChange={(e) => {
                      const next = e.target.checked
                        ? [...tempFloors, floor]
                        : tempFloors.filter(f => f !== floor);
                      setTempFloors(next);
                    }}
                    style={{ width: '100%' }}
                  >
                    <span style={{ color: checked ? '#1677ff' : 'inherit', fontWeight: checked ? 500 : 'normal' }}>
                      {label}
                    </span>
                  </Checkbox>
                </div>
              );
            })}
          </div>
        </Col>

        {/* Cột 3: Loại mặt bằng */}
        <Col span={8}>
          <div style={{ fontWeight: 600, marginBottom: 12, fontSize: '13px', color: '#111' }}>Loại mặt bằng</div>
          <div style={{ maxHeight: '130px', overflowY: 'auto', paddingRight: '4px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {allTypes.map(type => {
              const checked = tempTypes.includes(type);
              return (
                <div
                  key={type}
                  onClick={() => {
                    const next = checked
                      ? tempTypes.filter(t => t !== type)
                      : [...tempTypes, type];
                    setTempTypes(next);
                  }}
                  style={{
                    border: `1px solid ${checked ? '#1677ff' : '#d9d9d9'}`,
                    backgroundColor: checked ? '#e6f4ff' : '#fff',
                    color: checked ? '#1677ff' : 'rgba(0, 0, 0, 0.88)',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    cursor: 'pointer',
                    fontSize: '13px',
                    userSelect: 'none',
                    transition: 'all 0.2s',
                    gap: '4px',
                    fontWeight: checked ? 500 : 'normal'
                  }}
                >
                  {checked ? '✓' : ''} {type}
                </div>
              );
            })}
          </div>
        </Col>
      </Row>

      <Divider style={{ margin: '12px 0' }} />

      <div>
        <div style={{ fontWeight: 600, marginBottom: 8, fontSize: '13px', color: '#111' }}>Diện tích (m²)</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <InputNumber
            placeholder="Từ m²"
            value={tempMinArea}
            onChange={(val) => setTempMinArea(val)}
            style={{ width: '100%' }}
            min={0}
          />
          <span style={{ color: '#bfbfbf' }}>-</span>
          <InputNumber
            placeholder="Đến m²"
            value={tempMaxArea}
            onChange={(val) => setTempMaxArea(val)}
            style={{ width: '100%' }}
            min={0}
          />
        </div>
      </div>

      <Divider style={{ margin: '12px 0' }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button type="primary" danger onClick={handleClearFilters}>
          Xóa bộ lọc
        </Button>
        <Space size={8}>
          <Button onClick={handleCancel}>Hủy</Button>
          <Button type="primary" onClick={handleApply}>
            Áp dụng
          </Button>
        </Space>
      </div>
    </div>
  );

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
        {selectedStatuses.map(status => renderFilterTag(status, () => handleRemoveStatus(status)))}
        {selectedFloors.map(floor => renderFilterTag(floor === 0 ? "Tầng trệt" : `Tầng ${floor}`, () => handleRemoveFloor(floor)))}
        {selectedTypes.map(type => renderFilterTag(type, () => handleRemoveType(type)))}
        {minArea !== null && minArea !== "" && renderFilterTag(`Diện tích từ: ${minArea} m²`, handleRemoveMinArea)}
        {maxArea !== null && maxArea !== "" && renderFilterTag(`Diện tích đến: ${maxArea} m²`, handleRemoveMaxArea)}

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
        subtitle={role === ROLE.KHACH_THUE ? "Danh sách mặt bằng còn trống để gửi yêu cầu thuê thêm." : "Quản lý trạng thái và thông tin mặt bằng."}
        breadcrumb={["Mặt bằng"]}
        actionText={canWrite ? "Thêm mặt bằng" : null}
        actionIcon={<PlusOutlined />}
        onAction={canWrite ? () => setOpen(true) : undefined}
      />

      <Card className="toolbar-card" bordered={false} style={{ marginBottom: '16px' }} styles={{ body: { padding: '16px' } }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Input
            allowClear
            prefix={<SearchOutlined />}
            placeholder="Tìm kiếm mã hoặc vị trí mặt bằng..."
            value={keyword}
            onChange={(e) => {
              const val = e.target.value;
              setKeyword(val);
              applyFilters({ keyword: val || undefined }, !val);
            }}
            onPressEnter={handleKeywordSearch}
            style={{ width: 340 }}
          />

          <Button icon={<ReloadOutlined />} onClick={handleReload} style={{ minWidth: 100 }}>
            Tải lại
          </Button>

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
                minWidth: 100,
                justifyContent: 'center',
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
        </div>
        {renderActiveTags()}
      </Card>

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
