IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'MedicalRecordSystem')
BEGIN
    CREATE DATABASE MedicalRecordSystem;
END
GO

USE MedicalRecordSystem;
GO

-- 1. Bảng Doctors
IF OBJECT_ID('Doctors', 'U') IS NULL
CREATE TABLE Doctors (
    maBacSi VARCHAR(20) PRIMARY KEY,
    tenBacSi NVARCHAR(100) NOT NULL,
    chuyenKhoa NVARCHAR(100) NOT NULL
);

-- 2. Bảng Patients
IF OBJECT_ID('Patients', 'U') IS NULL
CREATE TABLE Patients (
    maBenhNhan VARCHAR(20) PRIMARY KEY,
    soCCCD CHAR(12) NOT NULL UNIQUE,
    hoVaTen NVARCHAR(100) NOT NULL,
    ngaySinh DATE NOT NULL,
    gioiTinh NVARCHAR(10) NOT NULL CHECK (gioiTinh IN (N'Nam', N'Nữ')),
    sdt VARCHAR(15) NOT NULL,
    diaChi NVARCHAR(255) NOT NULL
);

-- 3. Bảng Users
IF OBJECT_ID('Users', 'U') IS NULL
CREATE TABLE Users (
    tenDangNhap VARCHAR(50) PRIMARY KEY, 
    matKhau VARCHAR(255) NOT NULL,
    vaiTro NVARCHAR(20) NOT NULL CHECK (vaiTro IN (N'Bác sĩ', N'Bệnh nhân')),
    maBacSi VARCHAR(20) NULL,
    maBenhNhan VARCHAR(20) NULL,
    CONSTRAINT FK_Users_Doctors FOREIGN KEY (maBacSi) REFERENCES Doctors(maBacSi),
    CONSTRAINT FK_Users_Patients FOREIGN KEY (maBenhNhan) REFERENCES Patients(maBenhNhan)
);

-- 4. Bảng MedicalRecords
IF OBJECT_ID('MedicalRecords', 'U') IS NULL
CREATE TABLE MedicalRecords (
    maCaKham VARCHAR(20) PRIMARY KEY,
    maBenhNhan VARCHAR(20) NOT NULL,
    maBacSi VARCHAR(20) NOT NULL,
    ngayKham DATETIME NOT NULL,
    chuyenKhoa NVARCHAR(100) NULL,
    trieuChung NVARCHAR(2000) NULL,
    chanDoan NVARCHAR(1000) NULL,
    ghiChuDonThuoc NVARCHAR(MAX) NULL,
    CONSTRAINT FK_MedicalRecords_Patients FOREIGN KEY (maBenhNhan) REFERENCES Patients(maBenhNhan),
    CONSTRAINT FK_MedicalRecords_Doctors FOREIGN KEY (maBacSi) REFERENCES Doctors(maBacSi)
);
GO

-- ==========================================
-- SEED DỮ LIỆU MẪU CHUẨN CHO AUTOMATION TEST
-- ==========================================
USE MedicalRecordSystem;
GO

-- 1. Seed Doctors
IF NOT EXISTS (SELECT 1 FROM Doctors WHERE maBacSi = 'BS_01')
    INSERT INTO Doctors (maBacSi, tenBacSi, chuyenKhoa) VALUES ('BS_01', N'Nguyễn Văn A', N'Nội tổng hợp');

IF NOT EXISTS (SELECT 1 FROM Doctors WHERE maBacSi = 'BS_02')
    INSERT INTO Doctors (maBacSi, tenBacSi, chuyenKhoa) VALUES ('BS_02', N'Trần Đăng Khoa', N'Nhi khoa');

-- 2. Seed Patients
IF NOT EXISTS (SELECT 1 FROM Patients WHERE maBenhNhan = 'BN_01')
    INSERT INTO Patients (maBenhNhan, soCCCD, hoVaTen, ngaySinh, gioiTinh, sdt, diaChi)
    VALUES ('BN_01', '012345678912', N'Trần Thị B', '1990-01-01', N'Nữ', '0987654321', N'Hà Nội');

IF NOT EXISTS (SELECT 1 FROM Patients WHERE maBenhNhan = 'BN_02')
    INSERT INTO Patients (maBenhNhan, soCCCD, hoVaTen, ngaySinh, gioiTinh, sdt, diaChi)
    VALUES ('BN_02', '074204927301', N'Nguyễn Thị Hằng', '1994-08-20', N'Nữ', '0548625931', N'Quận 2, Hồ Chí Minh');

-- 3. Seed Users
IF NOT EXISTS (SELECT 1 FROM Users WHERE tenDangNhap = 'BS_NguyenVanA')
    INSERT INTO Users (tenDangNhap, matKhau, vaiTro, maBacSi, maBenhNhan)
    VALUES ('BS_NguyenVanA', 'Password123!', N'Bác sĩ', 'BS_01', NULL);

IF NOT EXISTS (SELECT 1 FROM Users WHERE tenDangNhap = 'BS_TranDangKhoa')
    INSERT INTO Users (tenDangNhap, matKhau, vaiTro, maBacSi, maBenhNhan)
    VALUES ('BS_TranDangKhoa', 'abc123', N'Bác sĩ', 'BS_02', NULL);

IF NOT EXISTS (SELECT 1 FROM Users WHERE tenDangNhap = 'BN_TranThiB')
    INSERT INTO Users (tenDangNhap, matKhau, vaiTro, maBacSi, maBenhNhan)
    VALUES ('BN_TranThiB', 'PatientPass456!', N'Bệnh nhân', NULL, 'BN_01');

-- 4. Seed MedicalRecords
IF NOT EXISTS (SELECT 1 FROM MedicalRecords WHERE maCaKham = 'MK_001')
    INSERT INTO MedicalRecords (maCaKham, maBenhNhan, maBacSi, ngayKham, chuyenKhoa, trieuChung, chanDoan, ghiChuDonThuoc)
    VALUES (
        'MK_001',
        'BN_01',
        'BS_01',
        GETDATE(),
        N'Nội tổng hợp',
        N'Bệnh nhân than phiền đau đầu, chóng mặt và ho khan kéo dài 3 ngày nay. Có biểu hiện sốt nhẹ về chiều.',
        N'Viêm họng cấp và suy nhược cơ thể',
        N'- Amoxicillin 500mg: Ngày uống 2 lần, mỗi lần 1 viên sau ăn.'
    );
GO