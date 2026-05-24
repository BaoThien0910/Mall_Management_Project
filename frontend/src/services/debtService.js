import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";
export const debtService = {
  calculate(payload) { return apiClient.post("/cong-no/tinh-toan", payload); },
  list(params) { return apiClient.get(`/cong-no${buildQuery(params)}`); },
  myDebts(params) { return apiClient.get(`/cong-no/cua-toi${buildQuery(params)}`); },
};
