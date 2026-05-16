import axiosClient from './axiosClient';

function normalizeInvoiceList(data) {
  if (Array.isArray(data)) return data;
  if (data?.items && Array.isArray(data.items)) return data.items;
  return [];
}

export async function fetchInvoices(params = {}) {
  const { data } = await axiosClient.get('/finance/invoices', { params });
  return normalizeInvoiceList(data);
}

export async function createPayment(payload) {
  const { data } = await axiosClient.post('/finance/payments', payload);
  return data;
}

export async function importFinancialFile(formData) {
  const { data } = await axiosClient.post('/finance/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}
