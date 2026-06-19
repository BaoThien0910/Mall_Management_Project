# Patch frontend sau khi backend đã sửa công nợ + dashboard

Copy các file trong thư mục `src/` vào đúng vị trí frontend hiện tại.

Các thay đổi chính:
- Thêm route `/maintenance/chi-so-dien-nuoc`.
- Dashboard gọi `GET /dashboard/me`, không dùng số giả.
- Sidebar lấy badge đỏ từ `menu_badges` của dashboard API.
- Bỏ icon chuông trên header.
- Import Excel tài chính chỉ hướng dẫn: Tiền thuê, Phí bảo trì, Hoàn trả.
- Trang Công nợ hiển thị danh sách thiếu chỉ số điện nước / thiếu dữ liệu import.
- Trang Thông báo có Drawer xem nội dung chi tiết qua `GET /thong-bao/{ma_tb}`.
