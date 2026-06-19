import { apiClient } from "./apiClient";

export const dashboardService = {
  getMyDashboard() {
    return apiClient.get("/dashboard/me");
  },
};
