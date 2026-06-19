import { apiClient } from "./apiClient";

export const rbacService = {
  listRoles() {
    return apiClient.get("/rbac/vai-tro");
  },

  listPermissions() {
    return apiClient.get("/rbac/quyen");
  },

  getPermissionsByRole(maVaiTro) {
    return apiClient.get(`/rbac/vai-tro/${maVaiTro}/quyen`);
  },
};