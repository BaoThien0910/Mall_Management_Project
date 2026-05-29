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
};