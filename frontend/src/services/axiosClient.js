import axios from 'axios';

const axiosClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 🌟 THE INTERCEPTOR 🌟
// Before any request leaves the app, intercept it and attach the token!
axiosClient.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('token');
    if (token) {
      // This is the exact format Python FastAPI expects!
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default axiosClient;