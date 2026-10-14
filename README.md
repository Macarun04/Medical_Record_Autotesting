# Medical Autotesting Project
Mô tả:
Xây dựng và triển khai hệ thống kiểm thử tự động cho website quản lý hồ sơ bệnh án điện tử
======================================
# Tổng hợp các bảng SQL cùng với thuộc tính của nó:
# Bảng 1: Users(Tài khoản & Phân quyền)
Thuộc tính || Kiểu dữ liệu SQL || Ràng buộc, ý nghĩa
- tenDangNhap: VARCHAR (50) NOT NULL, UNIQUE (Dùng làm ID đăng nhập)
- matKhau: VARCHAR(255) NOT NULL (lưu chuỗi mật khẩu)
- vaiTro: VARCHAR(20) NOT NULL (lưu giá trị Enum: 'Bác sĩ', 'Bệnh nhân', 'QA')

# Bảng 2: Patients/Bệnh nhân (Hồ sơ bệnh nhân)
Thuộc tính || Kiểu dữ liệu SQL || Ràng buộc, ý nghĩa
- maBenhNhan: VARCHAR(20) PRIMARY KEY (định danh riêng của bệnh nhân)
- soCCCD: CHAR(12) UNIQUE, NOT NULL (cố định 12 ký tự, giữ số 0 ở đầu)
- hoVaTen: NVARCHAR(100) NOT NULL (lưu tên tiếng việt có dấu)
- ngaySinh: DATE NOT NULL (lưu ngày tháng năm sinh)
- gioiTinh: NVARCHAR(10) NOT NULL (giá trị: 'Nam', 'Nữ')
- sdt: VARCHAR(15) cho phép NULL (lưu số đt dạng chuỗi)
- diaChi: NVARCHAR(255) cho phép NULL (địa chỉ liên hệ)
- doiTuongBHYT: VARCHAR(20) cho phép NULL (lưu mã thẻ BHYT)

# Bảng 3: MedicalRecords/Ca khám bệnh (Timeline)
Thuộc tính || Kiểu dữ liệu SQL || Ràng buộc, ý nghĩa
- maCaKham VARCHAR(20) PRIMARY KEY (định danh ca khám)
- maBenhNhan VARCHAR(20) NOT NULL (khóa ngoại tham chiếu bảng Patients)
- maBacSi VARCHAR(20) NOT NULL (khóa ngoại tham chiếu bảng Doctors/Users)
- maChuyenKhoa VARCHAR(20) NOT NULL (20) NOT NULL (khóa ngoại tham chiếu bảng Departments)
- ngayKham DATETIME NOT NULL (lưu thời gian khám để vẽ Timeline)
- trieuChung NVARCHAR(2000) cho phép NULL (mô tả triệu chứng lâm sàng)
- chanDoan NVARCHAR(1000) cho phép NULL (kết luận chẩn đoán)
- ghiChuDonThuoc NVARCHAR(MAX) cho phép NULL (đơn thuốc được gộp thành chuỗi text)

# Bảng 4: Departments (Danh mục chuyên khoa)
Thuộc tính || Kiểu dữ liệu SQL || Ràng buộc, ý nghĩa
- maChuyenKhoa VARCHAR(20) PRIMARY KEY
- tenChuyenKhoa NVARCHAR(100) NOT NULL (tên chuyên khoa hiển thị trên Dropdown)

# Bảng 5: Doctors (Danh mục Bác sĩ phụ trách)
- maBacSi VARCHAR(20) PRIMARY KEY
- tenBacSi NVARCHAR(100) NOT NULL (tên bác sĩ hiển thị trên Dropdown)

=======================================
# 4 màn hình UI cốt lõi (mô tả SUT):
# Màn hình 1: Đăng nhập và phân quyền

- Mục đích: Xác thực người dùng và phân quyền truy cập theo vai trò (Bác sĩ/Bệnh nhân/QA-Tester System)

- Input chính: 
    + tenDangNhap (Username/Email)
    + matKhau (Password)
    + vaiTro (Bác sĩ/Bệnh nhân)

- Output mong đợi:
    + Thành công: đăng nhập thành công, lưu JWT Token/Session, chuyển hướng đến màn hình trang chủ tương ứng với VaiTro
    + Thất bại: hộp thoại thông báo lỗi hiển thị rõ ràng ("Sai tài khoản hoặc mật khẩu", "Tài khoản bị khóa"...)

- Điều kiện biên:
    + Bỏ trống Username/Password
    + Kiểm tra phân quyền: Bệnh nhân cố tình truy cập URL trực tiếp của trang Bác sĩ (Redirect về 403 Forbidden hoặc Login)

--------------------------
# Màn hình 2: Tra cứu hồ sơ bệnh án qua CCCD

- Mục đích: cho phép Bác sĩ/Bệnh nhân tra cứu hồ sơ bệnh án bằng số CCCD

- Input chính: SoCCCD (Chuỗi 12 chữ số)

- Output mong đợi: 
    + Thành công: hiển thị hồ sơ bệnh án bệnh nhân 
        ++ Thông tin định danh:
            maBenhNhan (chuỗi định danh duy nhất)
            soCCCD (chuỗi 12 chữ số - dùng làm khóa chính)
            hoVaTen (chuỗi ký tự)
            ngaySinh
            gioiTinh
            sdt
            diaChi
            doiTuongBHYT (Số thẻ BHYT nếu có/tự nguyện)
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
    + maBenhNhan (hoặc SoCCCD)

- Output mong đợi:
    + Danh sách các thẻ ca khám xếp theo thứ tự thời gian giảm dần (ca khám mới nhất nằm ở trên cùng)
    + Chi tiết mỗi card ca khám bao gồm:
        Đầu trang (thông tin chung của bệnh nhân): 
            + maBenhNhan (chuỗi định danh duy nhất)
            + soCCCD (chuỗi 12 chữ số - dùng làm khóa chính)
            + hoVaTen (chuỗi ký tự)
            + ngaySinh
            + gioiTinh
            + sdt

        Bên dưới (danh sách các Card ca khám):
            + maCaKham
            + trangThai (trạng thái ca khám)
            + ngayKham

            + tenBacSi
            + trieuChung (triệu chứng lâm sàng - lý do khám)
            + chanDoan (chẩn đoán)
            + ghiChuDonThuoc

- Điều kiện biên:
    + Bệnh nhân mới tạo hồ sơ, chưa có lịch sử ca khám nào (Hiển thị empty state: "Chưa có dữ liệu ca khám")
    + Khoảng thời gian lọc không hợp lệ (TuNgay lớn hơn DenNgay)
    + Lọc theo khoảng thời gian không có ca khám nào phát sinh

--------------------------------
# Màn hình 4: Thêm ca khám mới 

- Mục đích: Bác sĩ nhập thông tin khám bệnh, chẩn đoán.. và tạo ca khám mới cho bệnh nhân

- Input chính:
    Đầu trang (thông tin chung của bệnh nhân): 
        + maBenhNhan
        + soCCCD
        + hoVaTen
        + ngaySinh
        + gioiTinh
        + sdt

    Bên dưới (danh sách các Card ca khám):
        + trangThai (trạng thái ca khám)
        + ngayKham

        + tenBacSi 
        + trieuChung (triệu chứng lâm sàng - lý do khám)
        + chanDoan (chẩn đoán)
        + ghiChuDonThuoc

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

# API 1 (Xác thực & Đăng nhập - API cung cấp Token để gọi các API khác): 
- Endpoint: /api/v1/auth/login 
- Method: POST - Cấp phát Token/Role phân quyền
- Request Body (JSON): 
    {
        "username": "BS_NguyenVanA",
        "password": "Password123!"
    }
- Response Body & HTTP Status Codes mong đợi:
    + 200 OK (đăng nhập thành công):
        {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "role": "Doctor",
            "userId": "BS001",
            "fullName": "Nguyễn Văn A"
        }

    + 401 Unauthorized (sai username hoặc password):
        { "message": "Sai tài khoản hoặc mật khẩu" }

    + 400 Bad Request (bỏ trống username/password)
----------------

# API 2 (Tra cứu hồ sơ qua CCCD): 
- Endpoint: /api/v1/patients/search
- Query Parameter: ?cccd={chuoi_12_so}
- Method: GET - Truy vấn thông tin bệnh nhân
- Request body: không có
- Response Body & HTTP Status Codes mong đợi:
    + 200 OK (tìm thấy bệnh nhân):
        {
            "maBenhNhan": "BN00102",
            "soCCCD": "012345678912",
            "hoVaTen": "Trần Thị B",
            "ngaySinh": "1990-05-20",
            "gioiTinh": "Nữ",
            "sdt": "0901234567",
            "diaChi": "Quận 1, TP.HCM",
            "doiTuongBHYT": "DN123456789"
        }
    
    + 404 Not found (không có bệnh nhân nào khớp CCCD)
        { "message": "Không tìm thấy hồ sơ bệnh nhân" }

    + 400 Bad Request (CCCD không đúng định dạng 12 số)
--------------

# API 3 (Lấy dữ liệu Timeline bệnh án - lấy toàn bộ lịch sử khám của một bệnh nhân, sắp xếp mới nhất lên đầu):
- Endpoint: /api/v1/patients/{maBenhNhan}/record
- Method: GET
- Path Variable: maBenhNhan 
- Request Body: không có
- Response Body & HTTP Status Codes mong đợi:
    + 200 OK (trả về mảng lịch sử khám. Nếu chưa từng khám thì trả về mảng rỗng []):
        {
            "maCaKham": "CK9981",
            "ngayKham": "2023-10-26T08:30:00Z",
            "tenBacSi": "Nguyễn Văn A",
            "trieuChung": "Đau đầu, sốt nhẹ",
            "chanDoan": "Sốt siêu vi",
            "ghiChuDonThuoc": "1. Paracetamol 500mg x 10 viên (Ngày 2 viên sáng tối)\n2. Oresol x 5 gói"
        }
    + 404 Not found (mã bệnh nhân không tồn tại trong hệ thống)
    + 401 Unauthorized (thiếu hoặc sai JWT Token)
----------------

# API 4 (Thêm ca khám mới - nhận dữ liệu form và lưu vào DB): 
- Endpoint: /api/v1/records
- Method: POST
- Request Body:
    {
        "maBenhNhan": "BN00102",
        "maBacSi": "BS001",
        "trieuChung": "Ho có đờm, rát họng",
        "chanDoan": "Viêm họng cấp",
        "ghiChuDonThuoc": "Kháng sinh Augmentin 1g x 14 viên..."
    }
- Response Body & HTTP Status Codes mong đợi:
    + 201 Created (lưu thành công, trả về ID ca khám để tiện cho PyTesst assert):
        {
            "maCaKham": "CK9982",
            "message": "Tạo ca khám thành công"
        }
    + 400 Bad Request (bỏ trống các trường bắt buộc như maBenhNhan, trieuChung, chanDoan)
    + 403 Forbidden (User là bệnh nhân nhưng cố tình gọi API tạo ca khám của bác sĩ)
-------------------

# API 5 (Tạo mới bệnh nhân - API ẩn - Test Data Setup)
- Endpoint: /api/v1/patients
- Method: POST
- Request body:
    {
        "soCCCD": "012345678912",
        "hoVaTen": "Trần Thị B",
        "ngaySinh": "1990-05-20",
        "gioiTinh": "Nữ",
        "sdt": "0901234567",
        "diaChi": "Quận 1, TP.HCM",
        "doiTuongBHYT": "DN123456789"
    }
- Response Body & HTTP Status Codes mong đợi:
    + 201 Created (tạo thành công, hệ thống tự sinh maBenhNhan):
        {
            "maBenhNhan": "BN00102",
            "message": "Tạo hồ sơ bệnh nhân thành công"
        }
    + 409 Conflict (trùng số CCCD đã tồn tại trong hệ thống)
    + 400 Bad Request (thiếu trường bắt buộc như họ tên, CCCD)   
----------------------            

# API 6 (Lấy danh sách Bác sĩ (bổ trợ UI) - API dùng để fill dữ liệu bác sĩ phụ trách): 
- Endpoint: /api/v1/doctors
- Method: GET
- Query Parameter (tùy chọn): ?departmentId=K01 (để lọc bác sĩ theo khoa nếu cần, không thì trả về hết)
- Request Body: không có
- Response Body & HTTP Status Codes mong đợi:
    + 200 OK:
        [
            { "maBacSi": "BS001", "tenBacSi": "Nguyễn Văn A" },
            { "maBacSi": "BS002", "tenBacSi": "Lê Thị C" }
        ]
