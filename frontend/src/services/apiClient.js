import axios from "axios";
import { message } from "antd";
import { clearAccessToken, getAccessToken } from "../utils/storage";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    const body = response.data;
    if (body && Object.prototype.hasOwnProperty.call(body, "success")) {
      return body.data;
    }
    return body;
  },
  (error) => {
    const status = error?.response?.status;
    const body = error?.response?.data;
    const backendMessage = body?.message || body?.detail;
    const finalMessage = backendMessage || "Không thể kết nối đến backend";

    if (status === 401) {
      clearAccessToken();
    }

    return Promise.reject({
      status,
      message: finalMessage,
      errors: body?.errors || [],
      raw: error,
    });
  }
);

export function showApiError(error) {
  message.error(error?.message || "Thao tác thất bại");
}
