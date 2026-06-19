import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";

export const incidentService = {
  create(payload) {
    return apiClient.post("/su-co-bao-tri", payload);
  },

  list(params) {
    return apiClient.get(`/su-co-bao-tri${buildQuery(params)}`);
  },

  review(maSuCo, payload) {
    return apiClient.patch(`/su-co-bao-tri/${maSuCo}/duyet`, payload);
  },

  assign(maSuCo, payload) {
    return apiClient.patch(`/su-co-bao-tri/${maSuCo}/phan-cong`, payload);
  },

  updateResult(maSuCo, payload) {
    return apiClient.patch(`/su-co-bao-tri/${maSuCo}/ket-qua`, payload);
  },

  updateCost(maSuCo, payload) {
    return apiClient.patch(`/su-co-bao-tri/${maSuCo}/chi-phi`, payload);
  },
};

export const maintenanceReportService = {
  create(payload) {
    return apiClient.post("/bao-cao-bao-tri", payload);
  },

  list(params) {
    return apiClient.get(`/bao-cao-bao-tri${buildQuery(params)}`);
  },

  detail(maBc) {
    return apiClient.get(`/bao-cao-bao-tri/${maBc}`);
  },

  exportExcel(maBc) {
    return apiClient.get(`/bao-cao-bao-tri/${maBc}/excel`, {
      responseType: "blob",
    });
  },
};
