import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";
export const notificationService = {
  create(payload) { return apiClient.post("/thong-bao", payload); },
  list(params) { return apiClient.get(`/thong-bao${buildQuery(params)}`); },
  detail(maTb) { return apiClient.get(`/thong-bao/${maTb}`); },
  revoke(maTb, payload) { return apiClient.patch(`/thong-bao/${maTb}/thu-hoi`, payload); },
};
