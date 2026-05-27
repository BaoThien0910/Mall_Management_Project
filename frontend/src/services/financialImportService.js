import { apiClient } from "./apiClient";
import { buildQuery } from "../utils/data";
export const financialImportService = {
  upload(file) {
    const form = new FormData();
    form.append("file", file);
    return apiClient.post("/import-tai-chinh", form);
  },
  list(params) { return apiClient.get(`/import-tai-chinh${buildQuery(params)}`); },
  deleteMany(ids) {
    return apiClient.post("/import-tai-chinh/batch-delete", { ids });
  },
};


