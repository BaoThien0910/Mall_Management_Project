import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";
export const financialImportService = {
  upload(file) {
    const form = new FormData();
    form.append("file", file);
    return apiClient.post("/import-tai-chinh", form, { headers: { "Content-Type": "multipart/form-data" } });
  },
  list(params) { return apiClient.get(`/import-tai-chinh${buildQuery(params)}`); },
};
