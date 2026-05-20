/* ============================================================
   Seed dữ liệu ban đầu để test Authentication + RBAC
   Dành cho SQL Server
   Mật khẩu test cho 2 tài khoản: admin1234

   Tài khoản:
   1) qtv_admin   / admin1234  bỏ
   2) bql_manager / admin1234  bỏ

   Lưu ý:
   - Chỉ dùng cho môi trường dev/test.
   - Nếu database của bạn không tên QL_TTTM, hãy đổi dòng USE.
   ============================================================ */
DROP DATABASE QLTTTM;
CREATE DATABASE QLTTTM;
USE QLTTTM;
GO

SET NOCOUNT ON;
GO

BEGIN TRY
    BEGIN TRANSACTION;

    /* ============================================================
       1. Seed VAITRO
       ============================================================ */

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.VAITRO
        WHERE MAVAITRO = 'QTV'
    )
    BEGIN
        INSERT INTO dbo.VAITRO (
            MAVAITRO,
            TENVAITRO,
            MOTA,
            TRANGTHAI
        )
        VALUES (
            'QTV',
            N'Quản trị viên',
            N'Quản trị toàn bộ hệ thống',
            N'Đang dùng'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.VAITRO
        WHERE MAVAITRO = 'BQL'
    )
    BEGIN
        INSERT INTO dbo.VAITRO (
            MAVAITRO,
            TENVAITRO,
            MOTA,
            TRANGTHAI
        )
        VALUES (
            'BQL',
            N'Ban Quản Lý',
            N'Vai trò quản lý nghiệp vụ tổng thể',
            N'Đang dùng'
        );
    END;

    /* ============================================================
       2. Seed QUYEN mẫu
       Các action phải tuân theo CHECK:
       Xem, Tạo, Sửa, Xóa, Duyệt, Thanh toán, Import
       ============================================================ */

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.QUYEN
        WHERE MAQUYEN = 'RBAC_VIEW'
    )
    BEGIN
        INSERT INTO dbo.QUYEN (
            MAQUYEN,
            TENQUYEN,
            MODULE,
            HANHDONG,
            MOTA
        )
        VALUES (
            'RBAC_VIEW',
            N'Xem danh sách vai trò và quyền',
            'RBAC',
            'Xem',
            N'Dùng để xem dữ liệu phân quyền'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.QUYEN
        WHERE MAQUYEN = 'RBAC_EDIT'
    )
    BEGIN
        INSERT INTO dbo.QUYEN (
            MAQUYEN,
            TENQUYEN,
            MODULE,
            HANHDONG,
            MOTA
        )
        VALUES (
            'RBAC_EDIT',
            N'Cập nhật quyền của vai trò',
            'RBAC',
            'Sửa',
            N'Dùng để gán lại danh sách quyền cho vai trò'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.QUYEN
        WHERE MAQUYEN = 'ACCOUNT_VIEW'
    )
    BEGIN
        INSERT INTO dbo.QUYEN (
            MAQUYEN,
            TENQUYEN,
            MODULE,
            HANHDONG,
            MOTA
        )
        VALUES (
            'ACCOUNT_VIEW',
            N'Xem danh sách tài khoản',
            'TAIKHOAN',
            'Xem',
            N'Dùng để xem danh sách tài khoản'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.QUYEN
        WHERE MAQUYEN = 'ACCOUNT_CREATE'
    )
    BEGIN
        INSERT INTO dbo.QUYEN (
            MAQUYEN,
            TENQUYEN,
            MODULE,
            HANHDONG,
            MOTA
        )
        VALUES (
            'ACCOUNT_CREATE',
            N'Tạo tài khoản',
            'TAIKHOAN',
            'Tạo',
            N'Dùng để tạo tài khoản mới'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.QUYEN
        WHERE MAQUYEN = 'PREMISE_VIEW'
    )
    BEGIN
        INSERT INTO dbo.QUYEN (
            MAQUYEN,
            TENQUYEN,
            MODULE,
            HANHDONG,
            MOTA
        )
        VALUES (
            'PREMISE_VIEW',
            N'Xem mặt bằng',
            'MATBANG',
            'Xem',
            N'Dùng để xem danh sách và chi tiết mặt bằng'
        );
    END;

    /* ============================================================
       3. Seed VAITRO_QUYEN
       QTV có toàn bộ quyền mẫu
       BQL chỉ có quyền xem mặt bằng để tạo khác biệt khi test
       ============================================================ */

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.VAITRO_QUYEN
        WHERE MAVAITRO = 'QTV'
          AND MAQUYEN = 'RBAC_VIEW'
    )
    BEGIN
        INSERT INTO dbo.VAITRO_QUYEN (
            MAVAITRO,
            MAQUYEN
        )
        VALUES (
            'QTV',
            'RBAC_VIEW'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.VAITRO_QUYEN
        WHERE MAVAITRO = 'QTV'
          AND MAQUYEN = 'RBAC_EDIT'
    )
    BEGIN
        INSERT INTO dbo.VAITRO_QUYEN (
            MAVAITRO,
            MAQUYEN
        )
        VALUES (
            'QTV',
            'RBAC_EDIT'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.VAITRO_QUYEN
        WHERE MAVAITRO = 'QTV'
          AND MAQUYEN = 'ACCOUNT_VIEW'
    )
    BEGIN
        INSERT INTO dbo.VAITRO_QUYEN (
            MAVAITRO,
            MAQUYEN
        )
        VALUES (
            'QTV',
            'ACCOUNT_VIEW'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.VAITRO_QUYEN
        WHERE MAVAITRO = 'QTV'
          AND MAQUYEN = 'ACCOUNT_CREATE'
    )
    BEGIN
        INSERT INTO dbo.VAITRO_QUYEN (
            MAVAITRO,
            MAQUYEN
        )
        VALUES (
            'QTV',
            'ACCOUNT_CREATE'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.VAITRO_QUYEN
        WHERE MAVAITRO = 'QTV'
          AND MAQUYEN = 'PREMISE_VIEW'
    )
    BEGIN
        INSERT INTO dbo.VAITRO_QUYEN (
            MAVAITRO,
            MAQUYEN
        )
        VALUES (
            'QTV',
            'PREMISE_VIEW'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.VAITRO_QUYEN
        WHERE MAVAITRO = 'BQL'
          AND MAQUYEN = 'PREMISE_VIEW'
    )
    BEGIN
        INSERT INTO dbo.VAITRO_QUYEN (
            MAVAITRO,
            MAQUYEN
        )
        VALUES (
            'BQL',
            'PREMISE_VIEW'
        );
    END;

    /* ============================================================
       4. Seed NHANVIEN
       ============================================================ */

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.NHANVIEN
        WHERE MANV = 'NV_QTV_001'
    )
    BEGIN
        INSERT INTO dbo.NHANVIEN (
            MANV,
            HOTEN,
            PHONGBAN,
            CHUCVU,
            SDT,
            EMAIL,
            TRANGTHAI
        )
        VALUES (
            'NV_QTV_001',
            N'Quản trị viên Seed',
            N'Quản trị hệ thống',
            N'Quản trị viên',
            '0900000001',
            'qtv.seed@example.local',
            N'Đang làm'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.NHANVIEN
        WHERE MANV = 'NV_BQL_001'
    )
    BEGIN
        INSERT INTO dbo.NHANVIEN (
            MANV,
            HOTEN,
            PHONGBAN,
            CHUCVU,
            SDT,
            EMAIL,
            TRANGTHAI
        )
        VALUES (
            'NV_BQL_001',
            N'Ban Quản Lý Seed',
            N'Ban Quản Lý',
            N'Ban Quản Lý',
            '0900000002',
            'bql.seed@example.local',
            N'Đang làm'
        );
    END;

    /* ============================================================
       5. Seed TAIKHOAN
       Hash bcrypt dưới đây dùng cho password: admin1234
       ============================================================ */

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.TAIKHOAN
        WHERE MATK = 'TK_QTV_001'
           OR TENDANGNHAP = 'qtv_admin'
    )
    BEGIN
        INSERT INTO dbo.TAIKHOAN (
            MATK,
            TENDANGNHAP,
            MATKHAU,
            TRANGTHAI,
            BATBUOC_DOIMK,
            SOLAN_DANGNHAPSAI,
            KHOA_DEN,
            MANV,
            MAKH,
            MAVAITRO
        )
        VALUES (
            'TK_QTV_001',
            'qtv_admin',
            '$2b$10$QkGQL1L00nBebiuIXlCYFOOBUVkTt/Z96.mHLWGAUDvNXsM1AxNbS',
            N'Hoạt động',
            0,
            0,
            NULL,
            'NV_QTV_001',
            NULL,
            'QTV'
        );
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.TAIKHOAN
        WHERE MATK = 'TK_BQL_001'
           OR TENDANGNHAP = 'bql_manager'
    )
    BEGIN
        INSERT INTO dbo.TAIKHOAN (
            MATK,
            TENDANGNHAP,
            MATKHAU,
            TRANGTHAI,
            BATBUOC_DOIMK,
            SOLAN_DANGNHAPSAI,
            KHOA_DEN,
            MANV,
            MAKH,
            MAVAITRO
        )
        VALUES (
            'TK_BQL_001',
            'bql_manager',
            '$2b$10$QkGQL1L00nBebiuIXlCYFOOBUVkTt/Z96.mHLWGAUDvNXsM1AxNbS',
            N'Hoạt động',
            0,
            0,
            NULL,
            'NV_BQL_001',
            NULL,
            'BQL'
        );
    END;

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
GO

/* ============================================================
   6. Query kiểm tra nhanh sau khi seed
   ============================================================ */

SELECT
    MAVAITRO,
    TENVAITRO,
    TRANGTHAI
FROM dbo.VAITRO
WHERE MAVAITRO IN ('QTV', 'BQL');

SELECT
    MAQUYEN,
    TENQUYEN,
    MODULE,
    HANHDONG
FROM dbo.QUYEN
WHERE MAQUYEN IN (
    'RBAC_VIEW',
    'RBAC_EDIT',
    'ACCOUNT_VIEW',
    'ACCOUNT_CREATE',
    'PREMISE_VIEW'
);

SELECT
    VTQ.MAVAITRO,
    VTQ.MAQUYEN
FROM dbo.VAITRO_QUYEN AS VTQ
WHERE VTQ.MAVAITRO IN ('QTV', 'BQL')
ORDER BY VTQ.MAVAITRO, VTQ.MAQUYEN;

SELECT
    MATK,
    TENDANGNHAP,
    TRANGTHAI,
    MANV,
    MAVAITRO
FROM dbo.TAIKHOAN
WHERE MATK IN ('TK_QTV_001', 'TK_BQL_001');
GO
-- =========================
-- 1. Seed vai trò
-- =========================
INSERT INTO VAITRO (MAVAITRO, TENVAITRO, MOTA, TRANGTHAI)
VALUES
('QTV', N'Quản trị viên', N'Quản trị hệ thống', N'Đang dùng'),
('BQL', N'Ban Quản Lý', N'Ban quản lý trung tâm', N'Đang dùng'),
('TP_KDTC', N'Trưởng phòng Kinh doanh - Tài chính', N'Quản lý tài chính', N'Đang dùng'),
('NV_KDTC', N'Nhân viên Kinh doanh - Tài chính', N'Nhân viên tài chính', N'Đang dùng'),
('TP_VHBT', N'Trưởng phòng Vận hành - Bảo trì', N'Quản lý vận hành bảo trì', N'Đang dùng'),
('NV_VHBT', N'Nhân viên Vận hành - Bảo trì', N'Nhân viên vận hành bảo trì', N'Đang dùng'),
('KHACH_THUE', N'Khách thuê', N'Khách thuê mặt bằng', N'Đang dùng');
select * from VAITRO;

-- =========================
-- 2. Seed quyền mẫu
-- =========================
INSERT INTO QUYEN (MAQUYEN, TENQUYEN, MODULE, HANHDONG, MOTA)
VALUES
('Q_XEM_MB', N'Xem mặt bằng', 'MATBANG', N'Xem', N'Quyền xem mặt bằng'),
('Q_TAO_MB', N'Tạo mặt bằng', 'MATBANG', N'Tạo', N'Quyền tạo mặt bằng'),
('Q_DUYET_YC', N'Duyệt yêu cầu thuê thêm', 'YC_THUETHEM', N'Duyệt', N'Quyền duyệt yêu cầu thuê thêm'),
('Q_XEM_BC', N'Xem báo cáo', 'BAOCAO', N'Xem', N'Quyền xem báo cáo');

select * from QUYEN;
-- =========================
-- 3. Seed nhân viên
-- =========================
INSERT INTO NHANVIEN
(MANV, HOTEN, PHONGBAN, CHUCVU, SDT, EMAIL, TRANGTHAI, NGAYTAO)
VALUES
('NV_QTV_002', N'Admin Hệ Thống', N'Quản trị hệ thống', N'Quản trị viên', '0900000001', 'qtv@test.local', N'Đang làm', GETDATE()),
('NV_BQL_001', N'Ban Quản Lý Test', N'Ban Quản Lý', N'Ban Quản Lý', '0900000002', 'bql@test.local', N'Đang làm', GETDATE()),
('NV_TPKDTC_001', N'Trưởng phòng KDTC Test', N'Kinh doanh - Tài chính', N'Trưởng phòng', '0900000003', 'tp.kdtc@test.local', N'Đang làm', GETDATE()),
('NV_NVKDTC_001', N'Nhân viên KDTC Test', N'Kinh doanh - Tài chính', N'Nhân viên', '0900000004', 'nv.kdtc@test.local', N'Đang làm', GETDATE()),
('NV_TPVHBT_001', N'Trưởng phòng VHBT Test', N'Vận hành - Bảo trì', N'Trưởng phòng', '0900000005', 'tp.vhbt@test.local', N'Đang làm', GETDATE()),
('NV_VHBT_001', N'Nhân viên VHBT Test', N'Vận hành - Bảo trì', N'Nhân viên', '0900000006', 'nv.vhbt@test.local', N'Đang làm', GETDATE());
select * from NHANVIEN;

-- =========================
-- 4. Seed khách thuê
-- =========================
INSERT INTO KHACHTHUE
(MAKH, TENKHACH, CCCD_MST, SDT, EMAIL, DIACHI, TRANGTHAI, NGAYTAO)
VALUES
('KH_TEST_001', N'Công ty Khách Thuê Test', '0319999999', '0911111111', 'khach@test.local', N'Quận 1, TP.HCM', N'Đang thuê', GETDATE());
select * from KHACHTHUE;

-- =========================
-- 5. Seed tài khoản QTV đầu tiên
-- =========================
INSERT INTO TAIKHOAN
(MATK, TENDANGNHAP, MATKHAU, TRANGTHAI, BATBUOC_DOIMK, SOLAN_DANGNHAPSAI, KHOA_DEN, MANV, MAKH, MAVAITRO, NGAYTAO)
VALUES
(
    'TK_QTV_001',
    'qtv_admin',
    '$2b$12$NPubi2SYIiOiQv689LER.OfMnUfngJjeCNWT/tAQr9NBR7hRgKVKy',
    N'Hoạt động',
    0,
    0,
    NULL,
    'NV_QTV_002',
    NULL,
    'QTV',
    GETDATE()
);

select * from TAIKHOAN;