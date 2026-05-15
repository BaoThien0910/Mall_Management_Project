import axiosClient from './axiosClient';

export const MOCK_INVOICES = [
  {
    key: '1',
    invoiceNo: 'INV-2025-1042',
    debtId: 'DEB-2025-003',
    tenant: 'Highlands Coffee',
    period: '09/2025',
    amount: 28500000,
    paidAt: '2025-10-03',
    method: 'bank_transfer',
  },
  {
    key: '2',
    invoiceNo: 'INV-2025-0988',
    debtId: 'DEB-2025-002',
    tenant: 'Uniqlo',
    period: '10/2025',
    amount: 41000000,
    paidAt: '2025-10-28',
    method: 'vnpay',
  },
  {
    key: '3',
    invoiceNo: 'INV-2025-0910',
    debtId: 'DEB-2025-001',
    tenant: 'Starbucks',
    period: '09/2025',
    amount: 42000000,
    paidAt: '2025-10-01',
    method: 'momo',
  },
];

export async function fetchInvoices(params) {
  try {
    const { data } = await axiosClient.get('/finance/invoices', { params });
    return data;
  } catch {
    return MOCK_INVOICES;
  }
}

export async function createPayment(payload) {
  try {
    const { data } = await axiosClient.post('/finance/payments', payload);
    return data;
  } catch {
    return {
      success: true,
      transactionId: `TXN-${Date.now()}`,
      paidAt: new Date().toISOString(),
    };
  }
}

export async function importFinancialFile(formData) {
  try {
    const { data } = await axiosClient.post('/finance/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  } catch {
    return {
      success: true,
      imported: 12,
      errors: 0,
      message: 'Nhập dữ liệu thành công (mô phỏng)',
    };
  }
}
