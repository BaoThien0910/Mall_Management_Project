const LABELS = {
  '/admin': 'Quản trị',
  '/admin/accounts': 'Tài khoản',
  '/admin/logs': 'Nhật ký',
  '/tenant': 'Trang chủ',
  '/tenant/contract': 'Hợp đồng',
  '/tenant/billing': 'Công nợ & thanh toán',
  '/tenant/billing/import': 'Nhập liệu',
  '/tenant/billing/invoices': 'Hóa đơn',
  '/tenant/billing/pay': 'Thanh toán',
  '/tenant/maintenance': 'Sự cố',
  '/staff': 'Bàn làm việc',
  '/staff/premises': 'Mặt bằng',
  '/staff/contracts': 'Hợp đồng',
  '/staff/finance': 'Công nợ',
  '/staff/finance/import': 'Nhập tài chính',
  '/staff/finance/invoices': 'Hóa đơn',
  '/staff/maintenance': 'Vận hành',
  '/management': 'Tổng quan',
  '/management/approvals': 'Phê duyệt',
  '/management/reports': 'Báo cáo',
  '/management/announcements': 'Thông báo',
};

/** @param {string} pathname */
export function breadcrumbsFor(pathname) {
  const trimmed = pathname.split('?')[0];
  let acc = '';
  const crumbs = [];
  trimmed
    .split('/')
    .filter(Boolean)
    .forEach((seg) => {
      acc += `/${seg}`;
      const label =
        LABELS[acc] ||
        (/^DEB-/i.test(seg) ? seg : /^pay$/i.test(seg) ? 'Thanh toán' : /^result$/i.test(seg) ? 'Kết quả' : seg);
      crumbs.push({ title: label });
    });

  return crumbs.length ? crumbs : [{ title: 'Trang' }];
}
