import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";
export const rentRequestService = {
  create(payload) { return apiClient.post("/yeu-cau-thue-them", payload); },
  list(params) { return apiClient.get(`/yeu-cau-thue-them${buildQuery(params)}`); },
  myRequests(params) { return apiClient.get(`/yeu-cau-thue-them/cua-toi${buildQuery(params)}`); },
  review(maYc, payload) { return apiClient.patch(`/yeu-cau-thue-them/${maYc}/duyet`, payload); },
};
