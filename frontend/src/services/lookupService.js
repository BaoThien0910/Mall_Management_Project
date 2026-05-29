import { apiClient } from "./apiClient";

export const lookupService = {
  maintenancePremises() {
    return apiClient.get("/danh-muc/mat-bang-bao-tri");
  },

  vhbtEmployees() {
    return apiClient.get("/danh-muc/nhan-vien-vhbt");
  },
};