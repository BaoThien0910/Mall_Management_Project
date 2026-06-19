import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";
export const meterService = {
  create(payload) { return apiClient.post("/chi-so-dien-nuoc", payload); },
  list(params) { return apiClient.get(`/chi-so-dien-nuoc${buildQuery(params)}`); },
};
