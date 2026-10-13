# Medical Autotesting Project
Mô tả:
Xây dựng và triển khai hệ thống kiểm thử tự động cho website quản lý hồ sơ bệnh án điện tử
======================================
# 4 màn hình UI cốt lõi (mô tả SUT):
# Màn hình 1: Đăng nhập và phân quyền

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

--------------------------
# Màn hình 2: Tra cứu hồ sơ bệnh án qua CCCD

- Mục đích: cho phép Bác sĩ/Bệnh nhân tra cứu hồ sơ bệnh án bằng số CCCD

- Input chính: SoCCCD (Chuỗi 12 chữ số)

- Output mong đợi: 
    + Thành công: hiển thị hồ sơ bệnh án bệnh nhân 
        ++ Thông tin định danh:
            MaBenhNhan (chuỗi định danh duy nhất): NVARCHAR(n)
            SoCCCD (chuỗi 12 chữ số - dùng làm khóa chính): NVARCHAR(12)
            HoVaTen (chuỗi ký tự): NVARCHAR(n)
            NgaySinh: date
            GioiTinh: NVARCHAR(n)
            Sdt:
            DiaChi: NVARCHAR(n)
            DoiTuongBHYT (Số thẻ BHYT nếu có/tự nguyện):
    + Thất bại: thông báo "Không tìm thấy dữ liệu bệnh nhân với số CCCD này"

- Điều kiện biên:
    + Nhập SoCCCD không đủ 12 số hoặc vượt quá 12 số 
    + Nhập SoCCCD chứa ký tự chữ cái hoặc ký tự đặc biệt
    + Tra cứu với số CCCD hợp lệ nhưng chưa từng khám tại hệ thống
    + Để trống ô tìm hiếm mà vẫn bấm nút Tra cứu (Tìm kiếm)

------------------------------
# Màn hình 3: Timeline bệnh án

- Mục đích: hiển thị toàn bộ lịch sử các ca khám bệnh của bệnh nhân theo trình tự thời gian

- Input chính: 
    + MaBenhNhan (hoặc SoCCCD)
    + TuNgay - DenNgay (Date Picker - bộ lọc thời gian)

- Output mong đợi:
    + Danh sách các thẻ ca khám xếp theo thứ tự thời gian giảm dần (ca khám mới nhất nằm ở trên cùng)
    + Chi tiết mỗi card ca khám bao gồm:
        Đầu trang (thông tin chung của bệnh nhân): MaBenhNhan, SoCCCD, HoVaTen, NgaySinh, GioiTinh

        Bên dưới (danh sách các Card ca khám):
            + MaCaKham
            + TrangThai (trạng thái ca khám)
            + NgayKham

            + ChuyenKhoa (tên chuyên khoa)
            + BacSi (tên bác sĩ phụ trách)
            + TrieuChung (triệu chứng lâm sàng - lý do khám)
            + ChanDoan (chẩn đoán)

            + DonThuoc:
                + TenThuoc
                + SoLuong
                + HuongDan (liều dùng)

- Điều kiện biên:
    + Bệnh nhân mới tạo hồ sơ, chưa có lịch sử ca khám nào (Hiển thị empty state: "Chưa có dữ liệu ca khám")
    + Khoảng thời gian lọc không hợp lệ (TuNgay lớn hơn DenNgay)
    + Lọc theo khoảng thời gian không có ca khám nào phát sinh

--------------------------------
# Màn hình 4: Thêm ca khám mới 

- Mục đích: Bác sĩ nhập thông tin khám bệnh, chẩn đoán.. và tạo ca khám mới cho bệnh nhân

- Input chính:
    Đầu trang (thông tin chung của bệnh nhân): 
        + MaBenhNhan
        + SoCCCD
        + HoVaTen
        + NgaySinh
        + GioiTinh

    Bên dưới (danh sách các Card ca khám):
        + TrangThai (trạng thái ca khám)
        + NgayKham

        + ChuyenKhoa (tên chuyên khoa)
        + BacSi (tên bác sĩ phụ trách)
        + TrieuChung (triệu chứng lâm sàng - lý do khám)
        + ChanDoan (chẩn đoán)

        + DonThuoc:
            + TenThuoc
            + SoLuong
            + HuongDan (liều dùng)

- Output mong đợi: 
    + Thành công: thông báo "Tạo ca khám thành công", hệ thống tự động sinh Mã ca khám mới và cập nhật ngay lập tức vào màn hình Timeline bệnh án

    + Thất bại: 

- Điều kiện biên:
    + Bỏ trống các trường bắt buộc (MaBenhNhan, SoCCCD, NgayKham...)
    + Kê đơn thuốc với số lượng âm hoặc bằng 0
    + Nhập nội dung TrieuChung chữa văn bản quá dài (> 2000 ký tự)
    + Bấm nút "Lưu ca khám" 2 lần liên tiếp (Double-click) -> Hệ thống chỉ ghi nhận 1 ca khám duy nhất

=====================================
# 6-8 API chính