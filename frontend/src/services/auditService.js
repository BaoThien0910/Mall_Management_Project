import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";
export const auditService = { list(params) { return apiClient.get(`/nhat-ky${buildQuery(params)}`); } };
