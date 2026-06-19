import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";
export const contractService = {
  list(params) { return apiClient.get(`/hop-dong${buildQuery(params)}`); },
  detail(maHd) { return apiClient.get(`/hop-dong/${maHd}`); },
  myContracts(params) { return apiClient.get(`/hop-dong/cua-toi${buildQuery(params)}`); },
  create(payload) { return apiClient.post("/hop-dong", payload); },
};
