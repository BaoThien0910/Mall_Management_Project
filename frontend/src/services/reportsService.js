import axiosClient from './axiosClient';

export async function getRevenueReport(params = {}) {
  const { data } = await axiosClient.get('/reports/revenue', { params });
  return data;
}

export async function getDebtReport(params = {}) {
  const { data } = await axiosClient.get('/reports/debt', { params });
  return data;
}

export async function getOccupancyReport(params = {}) {
  const { data } = await axiosClient.get('/reports/occupancy', { params });
  return data;
}

export async function getKPIDashboard(params = {}) {
  const { data } = await axiosClient.get('/reports/kpi', { params });
  return data;
}
