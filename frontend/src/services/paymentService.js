import { apiClient } from "./apiClient";
export const paymentService = {
  createSimulatedPayment(payload) { return apiClient.post("/thanh-toan/tao-giao-dich", payload); },
  detail(maHoaDon) { return apiClient.get(`/thanh-toan/${maHoaDon}`); },
  simulateResult(maHoaDon, payload) { return apiClient.post(`/thanh-toan/${maHoaDon}/mo-phong-ket-qua`, payload); },
};
