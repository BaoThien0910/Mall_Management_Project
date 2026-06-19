import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";

export const financialReportService = {
  create(payload) {
    return apiClient.post("/bao-cao-tai-chinh", payload);
  },

  list(params) {
    return apiClient.get(`/bao-cao-tai-chinh${buildQuery(params)}`);
  },

  detail(maBc) {
    return apiClient.get(`/bao-cao-tai-chinh/${maBc}`);
  },

  exportExcel(maBc) {
    return apiClient.get(`/bao-cao-tai-chinh/${maBc}/excel`, {
      responseType: "blob",
    });
  },
};
