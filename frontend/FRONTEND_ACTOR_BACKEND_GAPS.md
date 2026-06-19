# Các điểm sequence diagram chưa khớp backend hiện tại

Các chức năng bên dưới được đánh dấu để khoan làm sâu ở frontend cho đến khi backend được xác nhận/chỉnh lại.

## 1. Tên endpoint trong diagram khác backend

- Diagram: `/auth/login`; backend: `/auth/dang-nhap`.
- Diagram: `/taikhoan`; backend: `/tai-khoan`.
- Diagram: `/hopdong`; backend: `/hop-dong`.
- Diagram: `/yeucauthuemb`; backend: `/yeu-cau-thue-them`.
- Diagram: `/chisodiennuoc`; backend: `/chi-so-dien-nuoc`.
- Diagram: `/congno/tinh`; backend: `/cong-no/tinh-toan`.
- Diagram: `/thanhtoan`; backend: `/thanh-toan/tao-giao-dich` và `/thanh-toan/{ma_hoa_don}/mo-phong-ket-qua`.
- Diagram: `/sukien_baotri`; backend: `/su-co-bao-tri`.
- Diagram: `/baocao`; backend: `/bao-cao-tai-chinh/...`.
- Diagram: `/import-taichinh`; backend: `/import-tai-chinh`.

Frontend trong bộ này bám theo BACKEND hiện tại.

## 2. Tính công nợ trong diagram khác backend

Diagram thể hiện công nợ được tính từ:

- hợp đồng,
- chỉ số điện/nước,
- phí bảo trì,
- hoàn trả.

Backend hiện tại tính công nợ từ bảng `DULIEU_IMPORT_TAICHINH`, tức là phải import Excel trước rồi mới chạy `/cong-no/tinh-toan`.

Vì vậy frontend đã làm flow `Import tài chính -> Tính công nợ`, chưa làm flow tự tính trực tiếp từ chỉ số điện nước.

## 3. Thanh toán thật qua VNPay/MoMo chưa có

Diagram có lifeline cổng thanh toán VNPay/MoMo.
Backend hiện tại là thanh toán mô phỏng:

- tạo giao dịch: `/thanh-toan/tao-giao-dich`,
- mô phỏng kết quả: `/thanh-toan/{ma_hoa_don}/mo-phong-ket-qua`.

Frontend chỉ làm đúng flow mô phỏng.

## 4. Notification theo sự kiện chưa có backend riêng

Diagram có gửi thông báo tự động đến BQL, khách thuê, nhân viên.
Backend hiện tại chỉ có module `THONGBAO` để BQL ban hành/thu hồi thông báo; chưa có bảng thông báo cá nhân hoặc endpoint notification event.

Frontend chỉ làm màn hình thông báo chung, chưa làm notification realtime/event-based.

## 5. Báo cáo tài chính không có endpoint sửa bản nháp

Diagram có bước bổ sung ghi chú/xác nhận ban hành.
Backend hiện tại có:

- tạo báo cáo công nợ,
- tạo báo cáo doanh số,
- xem danh sách/chi tiết,
- ban hành.

Không có endpoint cập nhật/sửa bản nháp. Frontend không làm chức năng sửa báo cáo.
