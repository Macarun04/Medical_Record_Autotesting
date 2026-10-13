<<<<<<< HEAD
# Medical Autotesting Project
Mô tả:
Xây dựng và triển khai hệ thống kiểm thử tự động cho website quản lý hồ sơ bệnh án điện tử
=======
# DATN_ThanhBinh_Automation_Testing
Xây dựng và triển khai hệ thống kiểm thử tự động cho website quản lý hồ sơ bệnh án điện tử
--------------------------
4 màn hình UI cốt lõi (mô tả SUT):
* Màn hình 1: Đăng nhập và phân quyền

- Mục đích: Xác thực người dùng và phân quyền truy cập theo vai trò (Bác sĩ/Bệnh nhân/QA-Tester System)

- Input chính: 
    + TenDangNhap (Username/Email/Mã bác sĩ): NVARCHAR(n)
    + MatKhau (Password): NVARCHAR(n)
    + VaiTro (Bác sĩ/Bệnh nhân): NVARCHAR(n)

- Output mong đợi:
    + Thành công: đăng nhập thành công, lưu JWT Token/Session, chuyển hướng đến màn hình trang chủ tương ứng với VaiTro
    + Thất bại: hộp thoại thông báo lỗi hiển thị rõ ràng ("Sai tài khoản hoặc mật khẩu", "Tài khoản bị khóa"...)

- Điều kiện biên:
    + Bỏ trống Username/Password
    + Nhập sai mật khẩu quá 5 lần liên tiếp (khóa tạm thời)
    + Chèn chuỗi ký tự đặc biệt/SQL Injection/Script XSS vào ô đăng nhập
    + Kiểm tra phân quyền: Bệnh nhân cố tình truy cập URL trực tiếp của trang Bác sĩ (Redirect về 403 Forbidden hoặc Login)

* Màn hình 2: Tra cứu hồ sơ bệnh án qua CCCD

- Mục đích: cho phép Bác sĩ/Bệnh nhân tra cứu hồ sơ bệnh án bằng số CCCD

- Input chính: SoCCCD (Chuỗi 12 chữ số)

- Output mong đợi: 
    + Thành công: hiển thị hồ sơ bệnh án bệnh nhân 
        ++ Thông tin định danh:
            MaBenhNhan (chuỗi định danh duy nhất): NVARCHAR(n)
            SoCCCD (chuỗi 12 chữ số - dùng làm khóa chính): NVARCHAR(12)
            HoVaTen (chuỗi ký tự)
            DateBenhNhan
            GioiTinh
            Sdt
            DiaChi
            DoiTuongBHYT (Số thẻ BHYT nếu có/tự nguyện)

- Timeline bệnh án
- Thêm ca khám
>>>>>>> 4ab820f271d923bff16f88b26d4db422bbe08d87
