import { apiClient } from "./apiClient";

export const lookupService = {
  maintenancePremises() {
    return apiClient.get("/danh-muc/mat-bang-bao-tri");
  },

  vhbtEmployees() {
    return apiClient.get("/danh-muc/nhan-vien-vhbt");
  },

  accountEmployees() {
    return apiClient.get("/danh-muc/nhan-vien-tao-tai-khoan");
  },

  accountTenants() {
    return apiClient.get("/danh-muc/khach-thue-tao-tai-khoan");
  },

  contractTenants() {
    return apiClient.get("/danh-muc/khach-thue-hop-dong");
  },

  approvedRentRequestsForContract(maKhachThue) {
    return apiClient.get(
      `/danh-muc/yeu-cau-thue-them-hop-dong?ma_khach_thue=${encodeURIComponent(
        maKhachThue,
      )}`,
    );
  },

  vacantPremises() {
    return apiClient.get("/danh-muc/mat-bang-con-trong");
  },

  meterPremises() {
    return apiClient.get("/danh-muc/mat-bang-dien-nuoc");
  },
};
