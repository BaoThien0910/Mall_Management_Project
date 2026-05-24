import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";
export const financialReportService = {
  createDebtReport(payload) { return apiClient.post("/bao-cao-tai-chinh/cong-no", payload); },
  createRevenueReport(payload) { return apiClient.post("/bao-cao-tai-chinh/doanh-so", payload); },
  list(params) { return apiClient.get(`/bao-cao-tai-chinh${buildQuery(params)}`); },
  detail(maBctc) { return apiClient.get(`/bao-cao-tai-chinh/${maBctc}`); },
  publish(maBctc) { return apiClient.patch(`/bao-cao-tai-chinh/${maBctc}/ban-hanh`); },
};
