/*
  File: 03_seed_demo_data_latest.sql
  Mục đích: Insert dữ liệu demo/kiểm thử cho database QLTTTM theo thiết kế mới nhất.
  Điều kiện:
  - Chạy sau 02_init_all_tables_latest.sql, hoặc database hiện tại đã có schema mới nhất.
  - Schema mới KHÔNG có bảng LICHBT.
  - Báo cáo tài chính/bảo trì dùng thiết kế mới: BAOCAOTAICHINH + BAOCAOTAICHINH_CHITIET,
    BAOCAOBAOTRI + BAOCAOBAOTRI_CHITIET.

  Tài khoản demo dùng chung mật khẩu: Mk123456
  Ghi chú: MATKHAU bên dưới là bcrypt hash cho Mk123456.
*/

USE QLTTTM;
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRANSACTION;
GO

/* =========================================================
   0. XÓA DỮ LIỆU CŨ THEO THỨ TỰ KHÓA NGOẠI ĐỂ SEED LẠI
   ========================================================= */
DELETE FROM dbo.BAOCAOBAOTRI_CHITIET;
DELETE FROM dbo.BAOCAOTAICHINH_CHITIET;
DELETE FROM dbo.BAOCAOBAOTRI;
DELETE FROM dbo.BAOCAOTAICHINH;
DELETE FROM dbo.HOADON;
DELETE FROM dbo.CONGNO;
DELETE FROM dbo.DULIEU_IMPORT_TAICHINH;
DELETE FROM dbo.CHISODIENNUOC;
DELETE FROM dbo.SK_BAOTRI;
DELETE FROM dbo.THONGBAO;
DELETE FROM dbo.NHATKY;
DELETE FROM dbo.HOPDONG;
DELETE FROM dbo.YC_THUETHEM;
DELETE FROM dbo.VAITRO_QUYEN;
DELETE FROM dbo.TAIKHOAN;
DELETE FROM dbo.MATBANG;
DELETE FROM dbo.KHACHTHUE;
DELETE FROM dbo.NHANVIEN;
DELETE FROM dbo.QUYEN;
DELETE FROM dbo.VAITRO;
GO

/* =========================================================
   1. VAI TRÒ - QUYỀN
   ========================================================= */
INSERT INTO dbo.VAITRO (MAVAITRO, TENVAITRO, MOTA, TRANGTHAI)
VALUES
('QTV', N'Quản trị viên', N'Quản trị tài khoản và cấu hình hệ thống', N'Đang dùng'),
('BQL', N'Ban Quản Lý', N'Giám sát vận hành và duyệt nghiệp vụ', N'Đang dùng'),
('TP_KDTC', N'Trưởng phòng Kinh doanh - Tài chính', N'Quản lý tài chính, hợp đồng và báo cáo tài chính', N'Đang dùng'),
('NV_KDTC', N'Nhân viên Kinh doanh - Tài chính', N'Thực hiện nghiệp vụ hợp đồng và công nợ', N'Đang dùng'),
('TP_VHBT', N'Trưởng phòng Vận hành - Bảo trì', N'Quản lý vận hành, bảo trì và báo cáo bảo trì', N'Đang dùng'),
('NV_VHBT', N'Nhân viên Vận hành - Bảo trì', N'Nhập chỉ số, xử lý sự cố và cập nhật mặt bằng', N'Đang dùng'),
('KHACH_THUE', N'Khách thuê', N'Khách thuê mặt bằng trong trung tâm thương mại', N'Đang dùng');
GO

INSERT INTO dbo.QUYEN (MAQUYEN, TENQUYEN, MODULE, HANHDONG, MOTA)
VALUES
('Q_DASH_XEM', N'Xem dashboard', 'DASHBOARD', 'Xem', N'Xem màn hình tổng quan'),
('Q_TK_XEM', N'Xem tài khoản', 'TAI_KHOAN', 'Xem', N'Xem danh sách tài khoản'),
('Q_TK_TAO', N'Tạo tài khoản', 'TAI_KHOAN', 'Tạo', N'Tạo tài khoản người dùng'),
('Q_RBAC_XEM', N'Xem vai trò và phân quyền', 'RBAC', 'Xem', N'Xem vai trò và danh sách quyền'),
('Q_MB_XEM', N'Xem mặt bằng', 'MAT_BANG', 'Xem', N'Xem danh sách mặt bằng'),
('Q_HD_TAO', N'Số hóa hợp đồng', 'HOP_DONG', 'Tạo', N'Tạo/số hóa hợp đồng thuê'),
('Q_CN_XEM', N'Xem công nợ', 'CONG_NO', 'Xem', N'Xem danh sách công nợ'),
('Q_BCTC_TAO', N'Lập báo cáo tài chính', 'BAO_CAO_TAI_CHINH', 'Tạo', N'Lập báo cáo tài chính theo kỳ'),
('Q_SCBT_TAO', N'Gửi sự cố bảo trì', 'SU_CO_BAO_TRI', 'Tạo', N'Gửi yêu cầu xử lý sự cố'),
('Q_BCBT_TAO', N'Lập báo cáo bảo trì', 'BAO_CAO_BAO_TRI', 'Tạo', N'Lập báo cáo bảo trì theo kỳ');
GO

INSERT INTO dbo.VAITRO_QUYEN (MAVAITRO, MAQUYEN)
VALUES
('QTV', 'Q_DASH_XEM'),
('QTV', 'Q_TK_XEM'),
('QTV', 'Q_TK_TAO'),
('QTV', 'Q_RBAC_XEM'),
('BQL', 'Q_DASH_XEM'),
('BQL', 'Q_MB_XEM'),
('BQL', 'Q_CN_XEM'),
('TP_KDTC', 'Q_DASH_XEM'),
('TP_KDTC', 'Q_HD_TAO'),
('TP_KDTC', 'Q_CN_XEM'),
('TP_KDTC', 'Q_BCTC_TAO'),
('NV_KDTC', 'Q_HD_TAO'),
('TP_VHBT', 'Q_DASH_XEM'),
('TP_VHBT', 'Q_BCBT_TAO'),
('NV_VHBT', 'Q_MB_XEM'),
('KHACH_THUE', 'Q_SCBT_TAO');
GO

/* =========================================================
   2. NHÂN VIÊN - KHÁCH THUÊ - MẶT BẰNG - TÀI KHOẢN
   ========================================================= */
INSERT INTO dbo.NHANVIEN (MANV, HOTEN, PHONGBAN, CHUCVU, SDT, EMAIL, TRANGTHAI)
VALUES
('NV001', N'Nguyễn Quản Trị', N'Quản trị hệ thống', N'Quản trị viên', '0901000001', 'qtv@mall.local', N'Đang làm'),
('NV002', N'Trần Ban Quản Lý', N'Ban Quản Lý', N'Ban Quản Lý', '0901000002', 'bql@mall.local', N'Đang làm'),
('NV003', N'Lê Trưởng KDTC', N'Kinh doanh - Tài chính', N'Trưởng phòng', '0901000003', 'tp.kdtc@mall.local', N'Đang làm'),
('NV004', N'Phạm Nhân Viên KDTC', N'Kinh doanh - Tài chính', N'Nhân viên', '0901000004', 'nv.kdtc01@mall.local', N'Đang làm'),
('NV005', N'Hoàng Trưởng VHBT', N'Vận hành - Bảo trì', N'Trưởng phòng', '0901000005', 'tp.vhbt@mall.local', N'Đang làm'),
('NV006', N'Đỗ Nhân Viên VHBT 01', N'Vận hành - Bảo trì', N'Nhân viên', '0901000006', 'nv.vhbt01@mall.local', N'Đang làm'),
('NV007', N'Bùi Nhân Viên VHBT 02', N'Vận hành - Bảo trì', N'Nhân viên', '0901000007', 'nv.vhbt02@mall.local', N'Đang làm'),
('NV008', N'Vũ Nhân Viên KDTC 02', N'Kinh doanh - Tài chính', N'Nhân viên', '0901000008', 'nv.kdtc02@mall.local', N'Đang làm'),
('NV009', N'Ngô Nhân Viên VHBT 03', N'Vận hành - Bảo trì', N'Nhân viên', '0901000009', 'nv.vhbt03@mall.local', N'Đang làm');
GO

INSERT INTO dbo.KHACHTHUE (MAKH, TENKHACH, CCCD_MST, SDT, EMAIL, DIACHI, TRANGTHAI)
VALUES
('KH001', N'Công ty Thời Trang Sen Việt', 'MST000001', '0912000001', 'contact@senviet.local', N'12 Nguyễn Huệ, Quận 1', N'Đang thuê'),
('KH002', N'Cửa hàng Cafe Mây', 'MST000002', '0912000002', 'hello@cafemay.local', N'45 Lê Lợi, Quận 1', N'Đang thuê'),
('KH003', N'Nhà sách Sao Mai', 'MST000003', '0912000003', 'nhasach@saomai.local', N'20 Võ Văn Tần, Quận 3', N'Đang thuê'),
('KH004', N'Siêu thị Mini An Phúc', 'MST000004', '0912000004', 'info@anphuc.local', N'88 Cách Mạng Tháng 8, Quận 10', N'Đang thuê'),
('KH005', N'Spa Hoa Lan', 'MST000005', '0912000005', 'spa@hoalan.local', N'19 Pasteur, Quận 1', N'Đang thuê'),
('KH006', N'Điện máy Ánh Dương', 'MST000006', '0912000006', 'sales@anhduong.local', N'105 Điện Biên Phủ, Bình Thạnh', N'Đang thuê'),
('KH007', N'Nhà hàng Bếp Việt', 'MST000007', '0912000007', 'bepviet@food.local', N'77 Nguyễn Trãi, Quận 5', N'Đang thuê');
GO

INSERT INTO dbo.MATBANG (MAMB, VITRI, TANG, DIENTICH, LOAIMB, TRANGTHAI, GHICHU)
VALUES
('MB001', N'Khu A - Gian 01', 1, 80.00, N'Cửa hàng', N'Đang thuê', N'Gần cổng chính'),
('MB002', N'Khu A - Gian 02', 1, 65.00, N'Ẩm thực', N'Đang thuê', N'Gần thang cuốn'),
('MB003', N'Khu B - Gian 05', 2, 90.00, N'Cửa hàng', N'Đang thuê', N'Mặt tiền rộng'),
('MB004', N'Khu C - Gian 03', 3, 120.00, N'Siêu thị', N'Đang thuê', N'Khu đông khách'),
('MB005', N'Khu B - Gian 07', 2, 55.00, N'Dịch vụ', N'Đang thuê', N'Gần khu vui chơi'),
('MB006', N'Khu D - Gian 01', 4, 100.00, N'Điện máy', N'Đang thuê', N'Có kho phụ'),
('MB007', N'Khu F - Gian 02', 5, 110.00, N'Ẩm thực', N'Đang thuê', N'Khu nhà hàng'),
('MB008', N'Khu E - Gian 04', 4, 75.00, N'Cửa hàng', N'Đang thuê', N'Thuê thêm từ yêu cầu'),
('MB009', N'Khu G - Gian 01', 2, 70.00, N'Cửa hàng', N'Đang bảo trì', N'Đang sửa hệ thống đèn'),
('MB010', N'Khu H - Gian 06', 3, 85.00, N'Cửa hàng', N'Còn trống', N'Sẵn sàng cho thuê');
GO

DECLARE @DemoHash varchar(255) = '$2b$12$0N1zM/WZz972f7Ph6sLvr.ienbzqwXw0IESds37s7WIZldMpLBATu';

INSERT INTO dbo.TAIKHOAN (MATK, TENDANGNHAP, MATKHAU, TRANGTHAI, BATBUOC_DOIMK, SOLAN_DANGNHAPSAI, KHOA_DEN, MANV, MAKH, MAVAITRO)
VALUES
('TK001', 'qtv', @DemoHash, N'Hoạt động', 0, 0, NULL, 'NV001', NULL, 'QTV'),
('TK002', 'bql', @DemoHash, N'Hoạt động', 0, 0, NULL, 'NV002', NULL, 'BQL'),
('TK003', 'tp_kdtc', @DemoHash, N'Hoạt động', 0, 0, NULL, 'NV003', NULL, 'TP_KDTC'),
('TK004', 'nv_kdtc', @DemoHash, N'Hoạt động', 0, 0, NULL, 'NV004', NULL, 'NV_KDTC'),
('TK005', 'tp_vhbt', @DemoHash, N'Hoạt động', 0, 0, NULL, 'NV005', NULL, 'TP_VHBT'),
('TK006', 'nv_vhbt', @DemoHash, N'Hoạt động', 0, 0, NULL, 'NV006', NULL, 'NV_VHBT'),
('TK007', 'khachthue', @DemoHash, N'Hoạt động', 0, 0, NULL, NULL, 'KH001', 'KHACH_THUE');
GO

/* =========================================================
   3. YÊU CẦU THUÊ THÊM - HỢP ĐỒNG
   ========================================================= */
INSERT INTO dbo.YC_THUETHEM (MAYC, MAKH, MAMB, MANV_DUYET, NGAYGUI, LYDO, TRANGTHAI, NGAYDUYET, LYDO_TUCHOI, GHICHU)
VALUES
('YCT001', 'KH006', 'MB008', 'NV002', '2026-05-01T09:30:00', N'Mở rộng khu trưng bày điện máy', N'Đã tạo hợp đồng', '2026-05-02T14:00:00', NULL, N'Đã số hóa hợp đồng'),
('YCT002', 'KH002', 'MB010', NULL, '2026-05-20T10:15:00', N'Muốn mở thêm quầy cafe take-away', N'Chờ duyệt', NULL, NULL, NULL),
('YCT003', 'KH003', 'MB009', 'NV002', '2026-04-12T11:00:00', N'Muốn thuê mặt bằng đang sửa chữa', N'Từ chối', '2026-04-13T16:30:00', N'Mặt bằng đang trong giai đoạn bảo trì', NULL),
('YCT004', 'KH004', 'MB010', 'NV002', '2026-03-05T08:45:00', N'Mở rộng khu bán hàng gia dụng', N'Đã duyệt - Chờ số hóa hợp đồng', '2026-03-06T15:00:00', NULL, N'Chờ phòng KDTC số hóa'),
('YCT005', 'KH005', 'MB009', NULL, '2026-05-22T13:20:00', N'Mở thêm khu chăm sóc khách VIP', N'Chờ duyệt', NULL, NULL, NULL);
GO

INSERT INTO dbo.HOPDONG (MAHD, MAKH, MAMB, MANV_SOHOA, MAYC, NGAYBATDAU, NGAYKETTHUC, GIATHUETHANG, TRANGTHAI, NGAYSOHOA)
VALUES
('HD001', 'KH001', 'MB001', 'NV004', NULL, '2026-01-01', '2026-12-31', 25000000, N'Đang hiệu lực', '2026-01-01T09:00:00'),
('HD002', 'KH002', 'MB002', 'NV004', NULL, '2026-01-01', '2026-12-31', 32000000, N'Đang hiệu lực', '2026-01-02T09:00:00'),
('HD003', 'KH003', 'MB003', 'NV004', NULL, '2026-01-15', '2026-12-31', 28000000, N'Đang hiệu lực', '2026-01-15T09:00:00'),
('HD004', 'KH004', 'MB004', 'NV008', NULL, '2026-02-01', '2027-01-31', 45000000, N'Đang hiệu lực', '2026-02-01T09:00:00'),
('HD005', 'KH005', 'MB005', 'NV008', NULL, '2026-02-15', '2027-02-14', 18000000, N'Đang hiệu lực', '2026-02-15T09:00:00'),
('HD006', 'KH006', 'MB006', 'NV004', NULL, '2026-03-01', '2027-02-28', 22000000, N'Đang hiệu lực', '2026-03-01T09:00:00'),
('HD007', 'KH007', 'MB007', 'NV008', NULL, '2026-03-10', '2027-03-09', 35000000, N'Đang hiệu lực', '2026-03-10T09:00:00'),
('HD008', 'KH006', 'MB008', 'NV004', 'YCT001', '2026-05-03', '2027-05-02', 30000000, N'Đang hiệu lực', '2026-05-03T10:00:00');
GO

/* =========================================================
   4. NHẬT KÝ - THÔNG BÁO
   ========================================================= */
INSERT INTO dbo.NHATKY (MANHATKY, MATK, THOIGIAN, HANHDONG, DOITUONG, MADOITUONG, GIATRICU, GIATRIMOI, CHITIET, IP_ADDRESS)
VALUES
('NK001', 'TK001', '2026-05-01T08:00:00', N'Đăng nhập', N'TAIKHOAN', 'TK001', NULL, NULL, N'Quản trị viên đăng nhập', '127.0.0.1'),
('NK002', 'TK003', '2026-05-05T09:10:00', N'Tạo mới', N'HOPDONG', 'HD008', NULL, N'HD008', N'Số hóa hợp đồng thuê thêm', '127.0.0.1'),
('NK003', 'TK002', '2026-05-06T10:00:00', N'Duyệt', N'SK_BAOTRI', 'SC001', N'Chờ duyệt', N'Đã duyệt', N'Duyệt yêu cầu sự cố', '127.0.0.1'),
('NK004', 'TK005', '2026-05-06T14:30:00', N'Cập nhật', N'SK_BAOTRI', 'SC001', NULL, NULL, N'Phân công nhân viên xử lý', '127.0.0.1'),
('NK005', 'TK006', '2026-05-08T16:45:00', N'Cập nhật', N'SK_BAOTRI', 'SC001', NULL, NULL, N'Cập nhật kết quả xử lý', '127.0.0.1'),
('NK006', 'TK003', '2026-05-29T17:00:00', N'Tạo mới', N'BAOCAOTAICHINH', 'BCTC001', NULL, N'BCTC001', N'Lập báo cáo tài chính tháng 05/2026', '127.0.0.1'),
('NK007', 'TK005', '2026-05-29T17:10:00', N'Tạo mới', N'BAOCAOBAOTRI', 'BCBT001', NULL, N'BCBT001', N'Lập báo cáo bảo trì tháng 05/2026', '127.0.0.1');
GO

INSERT INTO dbo.THONGBAO (MATB, MANV_BANHANH, TIEUDE, NOIDUNG, LOAITHONGBAO, DOITUONGNHAN, NGAYBANHANH, TRANGTHAI)
VALUES
('TB001', 'NV002', N'Lịch kiểm tra PCCC tháng 05', N'Trung tâm sẽ kiểm tra hệ thống PCCC trong tháng 05.', N'Thông báo', N'Toàn hệ thống', '2026-05-01T08:00:00', N'Đã ban hành'),
('TB002', 'NV002', N'Quy định vận chuyển hàng hóa', N'Khách thuê vui lòng vận chuyển hàng theo khung giờ quy định.', N'Quy định', N'Khách thuê', '2026-05-03T09:00:00', N'Đã ban hành'),
('TB003', 'NV005', N'Kế hoạch bảo trì thang máy', N'Bộ phận VHBT sẽ bảo trì thang máy khu A.', N'Kế hoạch', N'Nội bộ', '2026-05-04T10:00:00', N'Đã ban hành'),
('TB004', 'NV002', N'Tạm ngưng cấp nước khu B', N'Khu B tạm ngưng cấp nước từ 22h đến 23h.', N'Thông báo', N'Khách thuê', '2026-05-10T15:00:00', N'Đã ban hành'),
('TB005', 'NV002', N'Thu hồi thông báo thử nghiệm', N'Thông báo thử nghiệm đã được thu hồi.', N'Thông báo', N'Nội bộ', '2026-04-20T08:00:00', N'Đã thu hồi');
GO

/* =========================================================
   5. ĐIỆN NƯỚC - IMPORT TÀI CHÍNH - CÔNG NỢ - THANH TOÁN
   ========================================================= */
INSERT INTO dbo.CHISODIENNUOC (MACSDN, MAMB, MANV_NHAP, THANG, NAM, CHISODIENDAU, CHISODIENCUOI, CHISONUOCDAU, CHISONUOCCUOI, NGAYNHAP)
VALUES
('CSDN001', 'MB001', 'NV006', 5, 2026, 1000, 1370, 500, 542, '2026-05-28T09:00:00'),
('CSDN002', 'MB002', 'NV006', 5, 2026, 1500, 1980, 620, 685, '2026-05-28T09:20:00'),
('CSDN003', 'MB003', 'NV007', 5, 2026, 1200, 1620, 430, 485, '2026-05-28T09:40:00'),
('CSDN004', 'MB004', 'NV007', 5, 2026, 2000, 2720, 800, 890, '2026-05-28T10:00:00'),
('CSDN005', 'MB005', 'NV009', 5, 2026, 900, 1140, 300, 330, '2026-05-28T10:20:00'),
('CSDN006', 'MB006', 'NV009', 5, 2026, 1300, 1590, 410, 443, '2026-05-28T10:40:00'),
('CSDN007', 'MB007', 'NV006', 5, 2026, 1700, 2280, 700, 778, '2026-05-28T11:00:00'),
('CSDN008', 'MB008', 'NV007', 5, 2026, 800, 1250, 260, 320, '2026-05-28T11:20:00');
GO

INSERT INTO dbo.DULIEU_IMPORT_TAICHINH (MAIMPORT, MAHD, THANG, NAM, LOAIKHOAN, SOTIEN, GHICHU, MANV_IMPORT, THOIGIAN_IMPORT, TENFILE, DONG_EXCEL, TRANGTHAI, LOI_CHITIET)
VALUES
('IMP001', 'HD001', 5, 2026, N'Tiền thuê', 25000000, N'Tiền thuê tháng 05', 'NV004', '2026-05-25T09:00:00', N'tai_chinh_05_2026.xlsx', 2, N'Đã dùng tính công nợ', NULL),
('IMP002', 'HD002', 5, 2026, N'Tiền thuê', 32000000, N'Tiền thuê tháng 05', 'NV004', '2026-05-25T09:00:00', N'tai_chinh_05_2026.xlsx', 3, N'Đã dùng tính công nợ', NULL),
('IMP003', 'HD003', 5, 2026, N'Hoàn trả', 500000, N'Điều chỉnh khuyến mãi', 'NV004', '2026-05-25T09:00:00', N'tai_chinh_05_2026.xlsx', 4, N'Đã dùng tính công nợ', NULL),
('IMP004', 'HD004', 5, 2026, N'Phí bảo trì', 1500000, N'Phí bảo trì tháng 05', 'NV008', '2026-05-25T09:15:00', N'tai_chinh_05_2026.xlsx', 5, N'Đã dùng tính công nợ', NULL),
('IMP005', 'HD005', 5, 2026, N'Tiền thuê', 18000000, N'Tiền thuê tháng 05', 'NV008', '2026-05-25T09:15:00', N'tai_chinh_05_2026.xlsx', 6, N'Hợp lệ', NULL),
('IMP006', 'HD006', 5, 2026, N'Tiền thuê', 22000000, N'Tiền thuê tháng 05', 'NV004', '2026-05-25T09:30:00', N'tai_chinh_05_2026.xlsx', 7, N'Hợp lệ', NULL),
('IMP007', 'HD007', 5, 2026, N'Hoàn trả', 1000000, N'Hoàn trả do điều chỉnh phí', 'NV008', '2026-05-25T09:30:00', N'tai_chinh_05_2026.xlsx', 8, N'Đã dùng tính công nợ', NULL),
('IMP008', 'HD008', 5, 2026, N'Tiền thuê', 30000000, N'Dòng cần kiểm tra lại', 'NV004', '2026-05-25T09:45:00', N'tai_chinh_05_2026.xlsx', 9, N'Lỗi', N'Dữ liệu demo dòng lỗi để kiểm thử xóa dòng lỗi');
GO

INSERT INTO dbo.CONGNO (MACN, MAHD, THANG, NAM, TIENTHUE, TIENDIEN, TIENNUOC, PHIBAOTRI, TIENHOAN, TONGTIEN, HAN_THANHTOAN, TRANGTHAI, NGAYLAP)
VALUES
('CN001', 'HD001', 5, 2026, 25000000, 1850000, 420000, 1000000, 0, 28270000, '2026-06-10', N'Đã thanh toán', '2026-05-29T08:00:00'),
('CN002', 'HD002', 5, 2026, 32000000, 2400000, 650000, 1200000, 0, 36250000, '2026-06-10', N'Đã thanh toán', '2026-05-29T08:05:00'),
('CN003', 'HD003', 5, 2026, 28000000, 2100000, 550000, 1000000, 500000, 31150000, '2026-06-10', N'Chưa thanh toán', '2026-05-29T08:10:00'),
('CN004', 'HD004', 5, 2026, 45000000, 3600000, 900000, 1500000, 0, 51000000, '2026-06-10', N'Chưa thanh toán', '2026-05-29T08:15:00'),
('CN005', 'HD005', 5, 2026, 18000000, 1200000, 300000, 800000, 0, 20300000, '2026-06-10', N'Đã thanh toán', '2026-05-29T08:20:00'),
('CN006', 'HD006', 5, 2026, 22000000, 1450000, 330000, 900000, 0, 24680000, '2026-06-10', N'Chưa thanh toán', '2026-05-29T08:25:00'),
('CN007', 'HD007', 5, 2026, 35000000, 2900000, 780000, 1300000, 1000000, 38980000, '2026-06-10', N'Đã thanh toán', '2026-05-29T08:30:00'),
('CN008', 'HD008', 5, 2026, 30000000, 2250000, 600000, 1000000, 0, 33850000, '2026-06-10', N'Chưa thanh toán', '2026-05-29T08:35:00');
GO

INSERT INTO dbo.HOADON (MAHOADON, MACN, MAKH, TIENTHUE, TIENDIEN, TIENNUOC, PHIBAOTRI, TIENHOAN, TONGTIEN, SOTIEN, PHUONGTHUC, MAGIAODICHCONG, THOIGIANGD, TRANGTHAI, NOIDUNG, GHICHU)
VALUES
('HDON001', 'CN001', 'KH001', 25000000, 1850000, 420000, 1000000, 0, 28270000, 28270000, N'VNPay', 'GDVNP001', '2026-05-30T09:00:00', N'Thành công', N'Thanh toán công nợ 05/2026', NULL),
('HDON002', 'CN002', 'KH002', 32000000, 2400000, 650000, 1200000, 0, 36250000, 36250000, N'MoMo', 'GDMOMO002', '2026-05-30T09:30:00', N'Thành công', N'Thanh toán công nợ 05/2026', NULL),
('HDON003', 'CN003', 'KH003', 28000000, 2100000, 550000, 1000000, 500000, 31150000, 31150000, N'ZaloPay', 'GDZLP003', '2026-05-30T10:00:00', N'Thất bại', N'Thanh toán công nợ 05/2026', N'Giao dịch thất bại'),
('HDON004', 'CN004', 'KH004', 45000000, 3600000, 900000, 1500000, 0, 51000000, 51000000, N'VNPay', 'GDVNP004', '2026-05-30T10:30:00', N'Đang xử lý', N'Thanh toán công nợ 05/2026', NULL),
('HDON005', 'CN005', 'KH005', 18000000, 1200000, 300000, 800000, 0, 20300000, 20300000, N'MoMo', 'GDMOMO005', '2026-05-30T11:00:00', N'Thành công', N'Thanh toán công nợ 05/2026', NULL),
('HDON006', 'CN006', 'KH006', 22000000, 1450000, 330000, 900000, 0, 24680000, 24680000, N'ZaloPay', 'GDZLP006', '2026-05-30T11:30:00', N'Thất bại', N'Thanh toán công nợ 05/2026', N'Khách hủy giao dịch'),
('HDON007', 'CN007', 'KH007', 35000000, 2900000, 780000, 1300000, 1000000, 38980000, 38980000, N'VNPay', 'GDVNP007', '2026-05-30T12:00:00', N'Thành công', N'Thanh toán công nợ 05/2026', NULL),
('HDON008', 'CN008', 'KH006', 30000000, 2250000, 600000, 1000000, 0, 33850000, 33850000, N'MoMo', 'GDMOMO008', '2026-05-30T12:30:00', N'Đang xử lý', N'Thanh toán công nợ 05/2026', NULL);
GO

/* =========================================================
   6. SỰ CỐ BẢO TRÌ
   ========================================================= */
INSERT INTO dbo.SK_BAOTRI (MASUCO, MAMB, MAKH, MANV_DUYET, MANV_PHANCONG, MANV_XULY, NGAYGUI, MOTA, TRANGTHAI, LYDO_TUCHOI, NGAYDUYET, NGAYPHANCONG, NGAYHOANTHANH, KETQUA, CHIPHI)
VALUES
('SC001', 'MB001', 'KH001', 'NV002', 'NV005', 'NV006', '2026-05-05T08:30:00', N'Đèn khu vực trưng bày bị chập chờn', N'Hoàn thành', NULL, '2026-05-05T10:00:00', '2026-05-05T14:00:00', '2026-05-06T16:00:00', N'Đã thay ballast và kiểm tra an toàn điện', 750000),
('SC002', 'MB002', 'KH002', 'NV002', 'NV005', 'NV007', '2026-05-06T09:15:00', N'Rò rỉ nước gần quầy pha chế', N'Hoàn thành', NULL, '2026-05-06T10:00:00', '2026-05-06T13:00:00', '2026-05-07T11:00:00', N'Đã thay ron và xử lý điểm rò', 650000),
('SC003', 'MB003', 'KH003', 'NV002', 'NV005', 'NV009', '2026-05-08T14:00:00', N'Máy lạnh không đủ mát', N'Đang xử lý', NULL, '2026-05-08T15:00:00', '2026-05-08T16:00:00', NULL, NULL, NULL),
('SC004', 'MB004', 'KH004', NULL, NULL, NULL, '2026-05-10T10:30:00', N'Cửa cuốn phát tiếng ồn khi đóng mở', N'Chờ duyệt', NULL, NULL, NULL, NULL, NULL, NULL),
('SC005', 'MB005', 'KH005', 'NV002', NULL, NULL, '2026-05-12T13:00:00', N'Yêu cầu thay đổi bảng hiệu ngoài phạm vi bảo trì', N'Từ chối', N'Nội dung không thuộc phạm vi bảo trì của trung tâm', '2026-05-12T15:00:00', NULL, NULL, NULL, NULL),
('SC006', 'MB006', 'KH006', 'NV002', 'NV005', 'NV006', '2026-04-04T08:00:00', N'Ổ cắm điện khu kho bị lỏng', N'Hoàn thành', NULL, '2026-04-04T09:00:00', '2026-04-04T10:00:00', '2026-04-04T16:00:00', N'Đã cố định ổ cắm và kiểm tra tải', 300000),
('SC007', 'MB007', 'KH007', 'NV002', 'NV005', 'NV007', '2026-04-10T11:00:00', N'Đường thoát nước bếp chậm', N'Hoàn thành', NULL, '2026-04-10T12:00:00', '2026-04-10T14:00:00', '2026-04-11T09:00:00', N'Đã thông đường thoát nước', 900000),
('SC008', 'MB008', 'KH006', 'NV002', 'NV005', 'NV009', '2026-05-15T09:00:00', N'Kệ trưng bày cần kiểm tra điểm cố định', N'Đã duyệt', NULL, '2026-05-15T10:00:00', NULL, NULL, NULL, NULL),
('SC009', 'MB009', 'KH003', 'NV002', 'NV005', 'NV006', '2026-03-22T09:00:00', N'Hệ thống đèn khu bảo trì cần kiểm tra', N'Hoàn thành', NULL, '2026-03-22T10:00:00', '2026-03-22T11:00:00', '2026-03-23T15:00:00', N'Đã thay dây nguồn và công tắc', 1200000),
('SC010', 'MB010', 'KH004', 'NV002', NULL, NULL, '2026-02-18T10:00:00', N'Kiểm tra hiện trạng trước khi thuê thêm', N'Từ chối', N'Mặt bằng chưa bàn giao cho khách thuê', '2026-02-18T15:30:00', NULL, NULL, NULL, NULL);
GO

/* =========================================================
   7. BÁO CÁO TÀI CHÍNH MỚI
   ========================================================= */
INSERT INTO dbo.BAOCAOTAICHINH (MABC, MANV, THANG, NAM, KYCHOT, NGAYLAP)
VALUES
('BCTC001', 'NV003', 5, 2026, '05/2026', '2026-05-29T17:00:00'),
('BCTC002', 'NV003', 4, 2026, '04/2026', '2026-04-29T17:00:00'),
('BCTC003', 'NV003', 3, 2026, '03/2026', '2026-03-29T17:00:00'),
('BCTC004', 'NV003', 2, 2026, '02/2026', '2026-02-27T17:00:00'),
('BCTC005', 'NV003', 1, 2026, '01/2026', '2026-01-29T17:00:00');
GO

INSERT INTO dbo.BAOCAOTAICHINH_CHITIET (MABC, STT, MAHD, MAKH, MAMB, KY, TIENTHUE, TIENDIEN, TIENNUOC, TIENHOANTRA, CHIPHI_BAOTRI, TONGTIEN, DA_THANH_TOAN, NO)
VALUES
('BCTC001', 1, 'HD001', 'KH001', 'MB001', '05/2026', 25000000, 1850000, 420000, 0, 1000000, 28270000, 28270000, 0),
('BCTC001', 2, 'HD002', 'KH002', 'MB002', '05/2026', 32000000, 2400000, 650000, 0, 1200000, 36250000, 36250000, 0),
('BCTC001', 3, 'HD003', 'KH003', 'MB003', '05/2026', 28000000, 2100000, 550000, 500000, 1000000, 31150000, 0, 31150000),
('BCTC001', 4, 'HD004', 'KH004', 'MB004', '05/2026', 45000000, 3600000, 900000, 0, 1500000, 51000000, 0, 51000000),
('BCTC001', 5, 'HD005', 'KH005', 'MB005', '05/2026', 18000000, 1200000, 300000, 0, 800000, 20300000, 20300000, 0),
('BCTC001', 6, 'HD006', 'KH006', 'MB006', '05/2026', 22000000, 1450000, 330000, 0, 900000, 24680000, 0, 24680000),
('BCTC001', 7, 'HD007', 'KH007', 'MB007', '05/2026', 35000000, 2900000, 780000, 1000000, 1300000, 38980000, 38980000, 0),
('BCTC001', 8, 'HD008', 'KH006', 'MB008', '05/2026', 30000000, 2250000, 600000, 0, 1000000, 33850000, 0, 33850000),
('BCTC002', 1, 'HD001', 'KH001', 'MB001', '04/2026', 25000000, 1700000, 410000, 0, 1000000, 28110000, 28110000, 0),
('BCTC002', 2, 'HD002', 'KH002', 'MB002', '04/2026', 32000000, 2300000, 620000, 0, 1200000, 36120000, 0, 36120000),
('BCTC003', 1, 'HD006', 'KH006', 'MB006', '03/2026', 22000000, 1300000, 300000, 0, 900000, 24500000, 24500000, 0),
('BCTC004', 1, 'HD004', 'KH004', 'MB004', '02/2026', 45000000, 3200000, 850000, 0, 1500000, 50550000, 0, 50550000),
('BCTC005', 1, 'HD001', 'KH001', 'MB001', '01/2026', 25000000, 1600000, 390000, 0, 1000000, 27990000, 27990000, 0);
GO

/* =========================================================
   8. BÁO CÁO BẢO TRÌ MỚI
   ========================================================= */
INSERT INTO dbo.BAOCAOBAOTRI (MABC, MANV, THANG, NAM, KYCHOT, NGAYLAP)
VALUES
('BCBT001', 'NV005', 5, 2026, '05/2026', '2026-05-29T17:10:00'),
('BCBT002', 'NV005', 4, 2026, '04/2026', '2026-04-29T17:10:00'),
('BCBT003', 'NV005', 3, 2026, '03/2026', '2026-03-29T17:10:00'),
('BCBT004', 'NV005', 2, 2026, '02/2026', '2026-02-27T17:10:00'),
('BCBT005', 'NV005', 1, 2026, '01/2026', '2026-01-29T17:10:00');
GO

INSERT INTO dbo.BAOCAOBAOTRI_CHITIET (MABC, STT, MAYC, MAMB, NGAYYC, MOTA, TRANGTHAI, NGAYGIAIQUYET, KETQUA)
VALUES
('BCBT001', 1, 'SC001', 'MB001', '2026-05-05T08:30:00', N'Đèn khu vực trưng bày bị chập chờn', N'Hoàn thành', '2026-05-06T16:00:00', N'Đã thay ballast và kiểm tra an toàn điện'),
('BCBT001', 2, 'SC002', 'MB002', '2026-05-06T09:15:00', N'Rò rỉ nước gần quầy pha chế', N'Hoàn thành', '2026-05-07T11:00:00', N'Đã thay ron và xử lý điểm rò'),
('BCBT001', 3, 'SC003', 'MB003', '2026-05-08T14:00:00', N'Máy lạnh không đủ mát', N'Đang xử lý', NULL, NULL),
('BCBT001', 4, 'SC004', 'MB004', '2026-05-10T10:30:00', N'Cửa cuốn phát tiếng ồn khi đóng mở', N'Chờ duyệt', NULL, NULL),
('BCBT001', 5, 'SC005', 'MB005', '2026-05-12T13:00:00', N'Yêu cầu thay đổi bảng hiệu ngoài phạm vi bảo trì', N'Từ chối', NULL, NULL),
('BCBT001', 6, 'SC008', 'MB008', '2026-05-15T09:00:00', N'Kệ trưng bày cần kiểm tra điểm cố định', N'Đã duyệt', NULL, NULL),
('BCBT002', 1, 'SC006', 'MB006', '2026-04-04T08:00:00', N'Ổ cắm điện khu kho bị lỏng', N'Hoàn thành', '2026-04-04T16:00:00', N'Đã cố định ổ cắm và kiểm tra tải'),
('BCBT002', 2, 'SC007', 'MB007', '2026-04-10T11:00:00', N'Đường thoát nước bếp chậm', N'Hoàn thành', '2026-04-11T09:00:00', N'Đã thông đường thoát nước'),
('BCBT003', 1, 'SC009', 'MB009', '2026-03-22T09:00:00', N'Hệ thống đèn khu bảo trì cần kiểm tra', N'Hoàn thành', '2026-03-23T15:00:00', N'Đã thay dây nguồn và công tắc'),
('BCBT004', 1, 'SC010', 'MB010', '2026-02-18T10:00:00', N'Kiểm tra hiện trạng trước khi thuê thêm', N'Từ chối', NULL, NULL);
GO

COMMIT TRANSACTION;
GO

SELECT N'SEED_DEMO_DATA_LATEST_DONE' AS RESULT;
GO
