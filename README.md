Cấu trúc thư mục frontend :

src/
├── assets/                         # Hình ảnh, icon, font chữ
├── components/                     # Component dùng chung
│   ├── common/                     # Button, Table, Modal, FormItem...
│   ├── layout/                     # Header, Sidebar, Breadcrumb
│   └── feedback/                   # Loading, ErrorMessage, EmptyState
├── layouts/                        # Layout theo nhóm người dùng
│   ├── AdminLayout.jsx
│   ├── ManagementLayout.jsx
│   ├── StaffLayout.jsx
│   └── TenantLayout.jsx
├── pages/
│   ├── auth/                       # Đăng nhập, đổi mật khẩu
│   ├── system/                     # Tài khoản, vai trò, quyền, audit log
│   ├── premises/                   # Mặt bằng, báo cáo trạng thái mặt bằng
│   ├── contracts/                  # Hợp đồng, yêu cầu thuê thêm
│   ├── finance/                    # Công nợ, hóa đơn, thanh toán, import Excel
│   │   ├── DebtListPage.jsx
│   │   ├── DebtDetailPage.jsx
│   │   ├── PaymentPage.jsx
│   │   ├── PaymentResultPage.jsx
│   │   ├── InvoiceHistoryPage.jsx
│   │   └── FinancialImportPage.jsx
│   ├── maintenance/                # Sự cố, phân công, lịch bảo trì
│   ├── reports/                    # Báo cáo tài chính, báo cáo bảo trì
│   └── notifications/              # Thông báo, kế hoạch, quy định
├── services/                       # Hàm gọi API theo module
│   ├── authService.js
│   ├── accountService.js
│   ├── roleService.js
│   ├── premiseService.js
│   ├── contractService.js
│   ├── debtService.js
│   ├── paymentService.js
│   ├── maintenanceService.js
│   ├── reportService.js
│   └── notificationService.js
├── store/                          # Redux store và slice
│   ├── authSlice.js
│   ├── permissionSlice.js
│   └── index.js
├── hooks/                          # Custom hooks
│   ├── useAuth.js
│   ├── usePermission.js
│   └── useApi.js
├── utils/                          # Tiện ích xử lý ngày, tiền tệ, enum
├── constants/                      # Hằng số, route, quyền, trạng thái
└── App.jsx                         # Khai báo route chính


Cấu trúc thư mục Backend:

app/
├── main.py                         # Khởi tạo FastAPI, đăng ký router
├── config.py                       # Cấu hình môi trường
├── database.py                     # Kết nối DB, session factory
├── dependencies.py                 # Dependency dùng chung
├── models/                         # ORM models
│   ├── taikhoan.py
│   ├── nhanvien.py
│   ├── khachthue.py
│   ├── vaitro.py
│   ├── quyen.py
│   ├── vaitro_quyen.py
│   ├── matbang.py
│   ├── hopdong.py
│   ├── yc_thuethem.py
│   ├── chisodiennuoc.py
│   ├── dulieu_import_taichinh.py
│   ├── congno.py
│   ├── hoadon.py
│   ├── baocaotaichinh.py
│   ├── sk_baotri.py
│   ├── lichbt.py
│   ├── baocaobaotri.py
│   ├── thongbao.py
│   └── nhatky.py
├── schemas/                        # Pydantic DTO
│   ├── auth.py
│   ├── taikhoan.py
│   ├── rbac.py
│   ├── matbang.py
│   ├── hopdong.py
│   ├── congno.py
│   ├── payment.py
│   ├── import_taichinh.py
│   ├── baotri.py
│   ├── baocao.py
│   └── thongbao.py
├── routers/                        # API endpoints
│   ├── auth.py
│   ├── taikhoan.py
│   ├── rbac.py
│   ├── matbang.py
│   ├── hopdong.py
│   ├── yc_thuethem.py
│   ├── chisodiennuoc.py
│   ├── congno.py
│   ├── payment.py
│   ├── import_taichinh.py
│   ├── baocaotaichinh.py
│   ├── sk_baotri.py
│   ├── lichbt.py
│   ├── baocaobaotri.py
│   ├── thongbao.py
│   └── nhatky.py
├── services/                       # Business logic
│   ├── auth_service.py
│   ├── account_service.py
│   ├── rbac_service.py
│   ├── premise_service.py
│   ├── contract_service.py
│   ├── rent_request_service.py
│   ├── meter_service.py
│   ├── billing_service.py
│   ├── payment_service.py
│   ├── excel_import_service.py
│   ├── financial_report_service.py
│   ├── maintenance_service.py
│   ├── maintenance_report_service.py
│   ├── notification_service.py
│   └── audit_service.py
│   └── email/
│       └── email_client.py
├── middleware/
│   ├── auth_middleware.py          # Xác thực JWT
│   ├── rbac_middleware.py          # Kiểm tra quyền theo RBAC
│   ├── audit_middleware.py         # Ghi nhật ký thao tác
│   └── exception_middleware.py     # Chuẩn hóa lỗi
├── utils/
│   ├── security.py                 # Băm mật khẩu, tạo token
│   ├── pagination.py               # Phân trang
│   ├── datetime.py                 # Xử lý ngày giờ
│   ├── money.py                    # Format tiền tệ
│   └── response.py                 # Chuẩn hóa response
└── tests/                          # Unit test và integration test
