export const TICKET_STATUS = {
  OPEN: 'open',
  IN_PROGRESS: 'in_progress',
  RESOLVED: 'resolved',
  CLOSED: 'closed',
};

export const TICKET_STATUS_LABELS = {
  open: 'Mở',
  in_progress: 'Đang xử lý',
  resolved: 'Đã giải quyết',
  closed: 'Đóng',
};

export const TICKET_STATUS_COLORS = {
  open: 'error',
  in_progress: 'processing',
  resolved: 'success',
  closed: 'default',
};

export const TICKET_PRIORITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  URGENT: 'urgent',
};

export const TICKET_PRIORITY_LABELS = {
  low: 'Thấp',
  medium: 'Trung bình',
  high: 'Cao',
  urgent: 'Khẩn cấp',
};

export const TICKET_PRIORITY_COLORS = {
  low: 'cyan',
  medium: 'blue',
  high: 'orange',
  urgent: 'red',
};

export const MAINTENANCE_CATEGORIES = [
  'Climate Control',
  'Plumbing',
  'Electrical',
  'Elevator',
  'Security',
  'Cleaning',
  'Fire Safety',
  'Structural',
  'Other',
];

export const TICKET_FILTERS = {
  STATUSES: Object.entries(TICKET_STATUS_LABELS).map(([key, label]) => ({
    label,
    value: key,
  })),
  PRIORITIES: Object.entries(TICKET_PRIORITY_LABELS).map(([key, label]) => ({
    label,
    value: key,
  })),
};
