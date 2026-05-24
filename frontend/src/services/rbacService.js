import { apiClient } from "./apiClient";

export const rbacService = {
  listRoles() { return apiClient.get("/rbac/vai-tro"); },
  listPermissions() { return apiClient.get("/rbac/quyen"); },
  getPermissionsByRole(maVaiTro) { return apiClient.get(`/rbac/vai-tro/${maVaiTro}/quyen`); },
  assignPermissions(maVaiTro, danhSachMaQuyen) { return apiClient.put(`/rbac/vai-tro/${maVaiTro}/quyen`, { danh_sach_ma_quyen: danhSachMaQuyen }); },
};
