import axios from 'axios';
import { store } from '../store';
import { logout } from '../store/authSlice';
import { clearCodes } from '../store/permissionSlice';

const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

const axiosClient = axios.create({
  baseURL: BASE.replace(/\/$/, ''),
  headers: {
    'Content-Type': 'application/json',
  },
});

axiosClient.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axiosClient.interceptors.response.use(
  (r) => r,
  (error) => {
    const status = error.response?.status;
    if (status === 401) {
      store.dispatch(logout());
      store.dispatch(clearCodes());
      if (!window.location.pathname.includes('/login')) {
        window.location.assign('/login');
      }
    }
    return Promise.reject(error);
  }
);

export default axiosClient;
