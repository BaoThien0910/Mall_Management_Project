import axiosClient from './axiosClient';

// MOCK: dùng khi API chưa sẵn sàng
export const MOCK_DEBTS = [
  {
    id: 'DEB-2025-001',
    tenant: 'Starbucks',
    premise: 'GF-01',
    period: '10/2025',
    dueDate: '2025-11-05',
    totalAmount: 45000000,
    paidAmount: 0,
    status: 'overdue',
  },
  {
    id: 'DEB-2025-002',
    tenant: 'Uniqlo',
    premise: 'L2-12',
    period: '10/2025',
    dueDate: '2025-11-10',
    totalAmount: 82000000,
    paidAmount: 41000000,
    status: 'partial',
  },
  {
    id: 'DEB-2025-003',
    tenant: 'Highlands Coffee',
    premise: 'GF-08',
    period: '09/2025',
    dueDate: '2025-10-05',
    totalAmount: 28500000,
    paidAmount: 28500000,
    status: 'paid',
  },
  {
    id: 'DEB-2025-004',
    tenant: 'Starbucks',
    premise: 'GF-01',
    period: '11/2025',
    dueDate: '2025-12-05',
    totalAmount: 45000000,
    paidAmount: 0,
    status: 'unpaid',
  },
];

export const MOCK_DEBT_DETAIL = {
  id: 'DEB-2025-001',
  tenant: 'Starbucks',
  premise: 'GF-01',
  period: '10/2025',
  dueDate: '2025-11-05',
  status: 'overdue',
  lines: [
    { key: '1', type: 'rent', description: 'Tiền thuê mặt bằng tháng 10/2025', amount: 38000000 },
    { key: '2', type: 'utility', description: 'Điện nước (chỉ số T10)', amount: 5200000 },
    { key: '3', type: 'service', description: 'Phí dịch vụ chung', amount: 1200000 },
    { key: '4', type: 'penalty', description: 'Phạt chậm trả (5 ngày)', amount: 600000 },
  ],
  totalAmount: 45000000,
  paidAmount: 0,
  note: 'Công nợ được tạo tự động từ hợp đồng HD-2024-089',
};

export async function fetchDebts(params) {
  try {
    const { data } = await axiosClient.get('/finance/debts', { params });
    return data;
  } catch {
    return MOCK_DEBTS;
  }
}

export async function fetchDebtById(id) {
  try {
    const { data } = await axiosClient.get(`/finance/debts/${id}`);
    return data;
  } catch {
    const found = MOCK_DEBTS.find((d) => d.id === id);
    return found
      ? { ...MOCK_DEBT_DETAIL, ...found, lines: MOCK_DEBT_DETAIL.lines }
      : { ...MOCK_DEBT_DETAIL, id };
  }
}

export async function calculateDebt(payload) {
  try {
    const { data } = await axiosClient.post('/finance/debts/calculate', payload);
    return data;
  } catch {
    return { success: true, message: 'Đã tính toán công nợ (mô phỏng)' };
  }
}
