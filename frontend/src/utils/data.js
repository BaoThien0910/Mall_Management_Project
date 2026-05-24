export function unwrapData(response) {
  if (!response) return null;
  if (Object.prototype.hasOwnProperty.call(response, "success")) return response.data;
  return response;
}

export function toArray(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.items)) return payload.items;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
}

export function pick(record, keys, fallback = "") {
  if (!record) return fallback;
  for (const key of keys) {
    if (record[key] !== undefined && record[key] !== null) return record[key];
  }
  return fallback;
}

export function pickId(record, candidates) {
  return pick(record, candidates, undefined);
}

export function formatMoney(value) {
  const n = Number(value || 0);
  return `${n.toLocaleString("vi-VN")} đ`;
}

export function formatDate(value) {
  if (!value) return "-";
  return String(value).slice(0, 10);
}

export function statusColor(status) {
  const s = String(status || "");
  if (["Hoạt động", "Đang hiệu lực", "Đã thanh toán", "Thành công", "Hoàn thành", "Đã ban hành", "Hợp lệ", "Đã tạo hợp đồng"].includes(s)) return "success";
  if (["Chờ duyệt", "Đang xử lý", "Chưa thanh toán", "Chưa thực hiện", "Bản nháp"].includes(s)) return "processing";
  if (["Từ chối", "Đã hủy", "Thất bại", "Vô hiệu", "Tạm khóa", "Lỗi"].includes(s)) return "error";
  if (["Quá hạn", "Đã duyệt", "Đã duyệt - Chờ số hóa hợp đồng", "Đang bảo trì"].includes(s)) return "warning";
  return "default";
}

export function buildQuery(params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") search.append(key, value);
  });
  const q = search.toString();
  return q ? `?${q}` : "";
}
