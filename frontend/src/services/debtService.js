import axiosClient from './axiosClient';

export function normalizeDebtList(data) {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.items)) return data.items;
  return [];
}

export async function fetchDebts(params = {}) {
  const { data } = await axiosClient.get('/finance/debts', { params });
  return normalizeDebtList(data);
}

export async function fetchDebtById(id) {
  const { data } = await axiosClient.get(`/finance/debts/${id}`);
  return data;
}

export async function calculateDebt(payload = {}) {
  const { data } = await axiosClient.post('/finance/debts/calculate', payload);
  return data;
}
