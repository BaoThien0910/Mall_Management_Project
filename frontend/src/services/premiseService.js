import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";
export const premiseService = {
  list(params) { return apiClient.get(`/mat-bang${buildQuery(params)}`); },
  detail(maMb) { return apiClient.get(`/mat-bang/${maMb}`); },
  create(payload) { return apiClient.post("/mat-bang", payload); },
  update(maMb, payload) { return apiClient.patch(`/mat-bang/${maMb}`, payload); },
  remove(maMb) { return apiClient.delete(`/mat-bang/${maMb}`); },
};
