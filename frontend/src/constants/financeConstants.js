export const DEBT_STATUS = {
  unpaid: { label: 'Chưa thanh toán', color: 'error' },
  partial: { label: 'Thanh toán một phần', color: 'warning' },
  paid: { label: 'Đã thanh toán', color: 'success' },
  overdue: { label: 'Quá hạn', color: 'red' },
};

export const PAYMENT_METHODS = [
  { value: 'bank_transfer', label: 'Chuyển khoản ngân hàng' },
  { value: 'momo', label: 'Ví MoMo' },
  { value: 'vnpay', label: 'VNPay' },
  { value: 'cash', label: 'Tiền mặt (tại quầy)' },
];

export const INVOICE_TYPES = {
  rent: 'Tiền thuê',
  service: 'Phí dịch vụ',
  utility: 'Điện nước',
  penalty: 'Phạt chậm trả',
};
