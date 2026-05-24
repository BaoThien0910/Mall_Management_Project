import { apiClient } from "./apiClient";

export const authService = {
  login(payload) {
    return apiClient.post("/auth/dang-nhap", payload);
  },
  logout() {
    return apiClient.post("/auth/dang-xuat");
  },
  changePassword(payload) {
    return apiClient.patch("/auth/doi-mat-khau", payload);
  },
  getCurrentUser() {
    return apiClient.get("/auth/thong-tin-hien-tai");
  },
};
