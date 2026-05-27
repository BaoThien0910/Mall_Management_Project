import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";

export const accountService = {
  list(params) { return apiClient.get(`/tai-khoan${buildQuery(params)}`); },
  create(payload) { return apiClient.post("/tai-khoan", payload); },
  disable(maTk, payload) { return apiClient.patch(`/tai-khoan/${maTk}/vo-hieu`, payload); },
  enable(maTk, payload) { return apiClient.patch(`/tai-khoan/${maTk}/khoi-phuc`, payload); },
};
