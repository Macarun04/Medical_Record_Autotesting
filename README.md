# Medical Autotesting Project
Mô tả:
Xây dựng và triển khai hệ thống kiểm thử tự động cho website quản lý hồ sơ bệnh án điện tử
======================================
# Tổng hợp các bảng SQL cùng với thuộc tính của nó:
# Bảng 1: Users(Tài khoản & Phân quyền)
Thuộc tính || Kiểu dữ liệu SQL || Ràng buộc, ý nghĩa
- tenDangNhap: VARCHAR (50) NOT NULL, UNIQUE (Dùng làm ID đăng nhập)
- matKhau: VARCHAR(255) NOT NULL (lưu chuỗi mật khẩu)
- vaiTro: VARCHAR(20) NOT NULL (lưu giá trị Enum: 'Bác sĩ', 'Bệnh nhân')
- maBacSi VARCHAR(20) NULL (khóa ngoại tham chiếu bảng Doctors)
- maBenhNhan: VARCHAR(20) NULL (khóa ngoại tham chiếu bảng Patients)

# Bảng 2: Patients/Bệnh nhân (Hồ sơ bệnh nhân)
Thuộc tính || Kiểu dữ liệu SQL || Ràng buộc, ý nghĩa
- maBenhNhan: VARCHAR(20) PRIMARY KEY (định danh riêng của bệnh nhân)
- soCCCD: CHAR(12) UNIQUE, NOT NULL (cố định 12 ký tự, giữ số 0 ở đầu)
- hoVaTen: NVARCHAR(100) NOT NULL (lưu tên tiếng việt có dấu)
- ngaySinh: DATE NOT NULL (lưu ngày tháng năm sinh)
- gioiTinh: NVARCHAR(10) NOT NULL (giá trị: 'Nam', 'Nữ')
- sdt: VARCHAR(15) cho phép NULL (lưu số đt dạng chuỗi)
- diaChi: NVARCHAR(255) cho phép NULL (địa chỉ liên hệ)

# Bảng 3: MedicalRecords/Ca khám bệnh (Timeline)
Thuộc tính || Kiểu dữ liệu SQL || Ràng buộc, ý nghĩa
- maCaKham VARCHAR(20) PRIMARY KEY (định danh ca khám)
- maBenhNhan VARCHAR(20) NOT NULL (khóa ngoại tham chiếu bảng Patients)
- maBacSi VARCHAR(20) NOT NULL (khóa ngoại tham chiếu bảng Doctors/Users)
- ngayKham DATETIME NOT NULL (lưu thời gian khám để vẽ Timeline)
- chuyenKhoa NVARCHAR(100) NULL (Lưu text tên khoa lúc khám)
- trieuChung NVARCHAR(2000) cho phép NULL (mô tả triệu chứng lâm sàng)
- chanDoan NVARCHAR(1000) cho phép NULL (kết luận chẩn đoán)
- ghiChuDonThuoc NVARCHAR(MAX) cho phép NULL (đơn thuốc được gộp thành chuỗi text)

# Bảng 4: Doctors (Danh mục Bác sĩ phụ trách)
- maBacSi VARCHAR(20) PRIMARY KEY
- tenBacSi NVARCHAR(100) NOT NULL (tên bác sĩ hiển thị trên Dropdown)
- chuyenKhoa NVARCHAR(100) NOT NULL (lưu tên chuyên khoa)

=======================================
# 4 màn hình UI cốt lõi (mô tả SUT):
# Màn hình 1: Đăng nhập và phân quyền

- Mục đích: Xác thực người dùng và phân quyền truy cập theo vai trò (Bác sĩ/Bệnh nhân/QA-Tester System)

- Input chính: 
    + tenDangNhap (Username/Email)
    + matKhau (Password)

- Output mong đợi:
    + Thành công: Hệ thống tự trích xuất vaiTro từ DB, lưu JWT Token/Session và chuyển hướng đến trang chủ tương ứng.
    + Thất bại: Thông báo lỗi chữ đỏ "Sai tài khoản hoặc mật khẩu".

- Điều kiện biên:
    + Bỏ trống Username/Password
    + Kiểm tra phân quyền: Bệnh nhân cố tình truy cập URL trực tiếp của trang Bác sĩ (Redirect về 403 Forbidden hoặc Login)

--------------------------
# Màn hình 2: Tra cứu hồ sơ bệnh án qua CCCD

- Mục đích: cho phép Bác sĩ tra cứu hồ sơ bệnh án bằng số CCCD

- Input chính: soCCCD (Chuỗi 12 chữ số)

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
    + Thất bại: thông báo "Không tìm thấy dữ liệu bệnh nhân với số CCCD này"

- Điều kiện biên:
    + Nhập soCCCD không đủ 12 số hoặc vượt quá 12 số 
    + Nhập soCCCD chứa ký tự chữ cái hoặc ký tự đặc biệt
    + Tra cứu với số CCCD hợp lệ nhưng chưa từng khám tại hệ thống
    + Để trống ô tìm hiếm mà vẫn bấm nút Tra cứu (Tìm kiếm)

------------------------------
# Màn hình 3: Timeline bệnh án

- Mục đích: hiển thị lịch sử các ca khám bệnh của bệnh nhân theo trình tự thời gian giảm dần (mới nhất ở trên)

- Input chính: 
    + maBenhNhan (Lấy ngầm từ URL hoặc sau khi tra cứu ở Màn hình 2)

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
            + diaChi

        Bên dưới (danh sách các Card ca khám):
                + maCaKham
                + ngayKham
                + tenBacSi
                + chuyenKhoa

                + trieuChung (triệu chứng lâm sàng - lý do khám)
                + chanDoan (chẩn đoán)
                + ghiChuDonThuoc

- Điều kiện biên:
    + Bệnh nhân mới tạo hồ sơ, chưa có lịch sử ca khám nào (Hiển thị empty state: "Chưa có dữ liệu ca khám")

--------------------------------
# Màn hình 4: Thêm ca khám mới 

- Mục đích: Bác sĩ nhập thông tin khám bệnh, chẩn đoán.. và tạo ca khám mới cho bệnh nhân

- Input chính:
        + chuyenKhoa (nhập tên khoa/chọn từ dropdown list)
        + trieuChung (triệu chứng lâm sàng - lý do khám)
        + chanDoan (chẩn đoán)
        + ghiChuDonThuoc

- Output mong đợi: 
    + Thành công: thông báo "Tạo ca khám thành công", hệ thống tự động sinh Mã ca khám mới và cập nhật ngay lập tức vào màn hình Timeline bệnh án

    + Thất bại: thông báo chữ đỏ cảnh báo thiếu trường dữ liệu.

- Điều kiện biên:
    + Bỏ trống các trường bắt buộc (Chuyên khoa, Triệu chứng, Chẩn đoán...)
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

# Testcase (kịch bản kiểm thử) riêng biệt của API 1 
# (POST /api/v1/auth/login)
-  TC_API1_01 (Happy Path - Luồng bác sĩ): gửi Request body JSON với tenDangNhap va matKhau hợp lệ của Bác sĩ. 
->  Kết quả: HTTP 200 OK
    Response Body trả về token, vaiTro là "Bác sĩ" và maBacSi trích xuất từ bảng Users

-  TC_API1_02 (Happy Path - Luồng bệnh nhân): gửi Request với tenDangNhap va matKhau hợp lệ của Bệnh nhân
->  Kết quả: HTTP 200 OK
    Response trả về Token, vaiTro là "Bệnh nhân" và maBenhNhan   

-  TC_API1_03 (Negative - Sai mật khẩu): gửi Request với tenDangNhap đúng nhưng matKhau sai.
->  Kết quả: HTTP 401 Unauthorized, Response trả về lỗi "Sai tài khoản/mật khẩu"

-  TC_API1_04 (Validation - dữ liệu trống): gửi Request bỏ trống trường tenDangNhap hoặc matKhau
->  Kết quả: HTTP 400 Bad Request; Báo lỗi thiếu dữ liệu đầu vào

-  TC_API1_05 (Validation - sai định dạng Payload): gửi Request body dạng chuỗi text thay vì chuẩn JSON. 
->  Kết quả: HTTP 400 Bad Request
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
        }
    
    + 404 Not found (không có bệnh nhân nào khớp CCCD)
        { "message": "Không tìm thấy hồ sơ bệnh nhân" }

    + 400 Bad Request (CCCD không đúng định dạng 12 số)

# Testcase (kịch bản kiểm thử) riêng biệt của API 2 
# (GET /api/v1/patients/search?cccd={soCCCD})
- TC_API2_01 (Happy Path): gửi Request với tham số ?cccd= chứa đúng 12 chữ số hợp lệ, có trong bảng Patients
->  Kết quả: HTTP 200 OK; Trả về Object JSON chứa maBenhNhan, soCCCD, hoVaTen, ngaySinh, gioiTinh, sdt, diaChi

- TC_API2_02 (Negative - không tồn tại): gửi Request với tham số cccd= gồm 12 số hợp lệ nhưng chưa từng đăng ký (chưa từng khám lần nào).
->  Kết quả: HTTP 404 Not Found; trả về lỗi "Không tìm thấy dữ liệu hồ sơ bệnh nhân với số CCCD này"

- TC_API2_03 (Validation - Sai độ dài): gửi Request với tham số ?cccd= chỉ có 9 số hoặc lên tới 13 số
->  Kết quả: HTTP 400 Bad Request

- TC_API2_04 (Validation - chưa ký tự lạ): gửi Request với tham số ?cccd= chứa chữ cái hoặc ký tự đặc biệt
->  KẾt quả: HTTP 400 Bad Request

- TC_API2_05 (Validation - thiếu tham số): gửi Request gọi endpoint nhưng không đính kèm query parameter ?cccd=
->  KẾt quả: HTTP 400 Bad Request

--------------

# API 3 (Lấy dữ liệu Timeline bệnh án - lấy toàn bộ lịch sử khám của một bệnh nhân, sắp xếp mới nhất lên đầu):
- Endpoint: /api/v1/patients/{maBenhNhan}/record
- Method: GET
- Path Variable: maBenhNhan 
- Request Body: không có
- Response Body & HTTP Status Codes mong đợi:
    + 200 OK (trả về mảng lịch sử khám. Nếu chưa từng khám thì trả về mảng rỗng []):
[
        {
        "maCaKham": "CK9981",
        "ngayKham": "2023-10-26T08:30:00Z",
        "chuyenKhoa": "Nội tổng hợp",
        "tenBacSi": "Nguyễn Văn A",
        "trieuChung": "Đau đầu, sốt nhẹ",
        "chanDoan": "Sốt siêu vi",
        "ghiChuDonThuoc": "1. Paracetamol 500mg x 10 viên (Ngày 2 viên sáng tối)\n2. Oresol x 5 gói"
    	}

]
    + 404 Not found (Mã bệnh nhân không tồn tại trong hệ thống): { "message": "Không tìm thấy hồ sơ bệnh nhân" }
    + 401 Unauthorized (thiếu hoặc sai JWT Token)

# Testcase (kịch bản kiểm thử) riêng biệt của API 3 
# (GET /api/v1/patients/{maBenhNhan}/record)
- TC_API3_01 (Happy Path - có dữ liệu): truyền Path Variable {maBenhNhan} hợp lệ của bệnh nhân đã có ca khám
->  Kết quả: HTTO 200 OK; Trả về mảng JSON (Array [] ) chứa các ca khám được sắp xếp ngayKham giảm dần, bao gồm trường chuyenKhoa

- TC_API3_02 (Happy Path- Empty State): truyền {maBenhNhan} hợp lệ của bệnh nhân mới tạo hồ sợ, chưa có lịch sử khám
->  Kết quả: HTTP 200 OK; Trả về mảng rỗng []

- TC_API3_03 (Negative - Không xác thực): truyền {maBenhNhan} không tồn tại trong bảng Patients
->  Kết quả: HTTP 404 Not Found

- TC_API3_04 (Security - Không xác thực): gọi API nhưng không đính kèm JWT Token ở HTTP Header
->  Kết quả: HTTP 401 Unauthorized

- TC_API3_05 (Security - SQL Injection): truyền {maBenhNhan} chứa câu lệnh SQL nhạy cảm (VD: BN01' OR '1'='1)
->  Kết quả: HTTP 400 Bad Request hoặc 404 Not Found (hệ thống chặn thành công)
----------------

# API 4 (Thêm ca khám mới - nhận dữ liệu form và lưu vào DB): 
- Endpoint: /api/v1/records
- Method: POST
- Request Body:
    	{
    "maBenhNhan": "BN00102",
    "maBacSi": "BS001",
    "chuyenKhoa": "Nội tổng hợp",
    "trieuChung": "Ho có đờm, rát họng",
    "chanDoan": "Viêm họng cấp",
    "ghiChuDonThuoc": "Kháng sinh Augmentin 1g x 14 viên..."
	}
- Response Body & HTTP Status Codes mong đợi:
    + 201 Created (lưu thành công, trả về ID ca khám để tiện cho PyTest assert):
        {
            "maCaKham": "CK9982",
            "message": "Tạo ca khám thành công"
        }
    + 400 Bad Request (bỏ trống các trường bắt buộc như maBenhNhan, chuyenKhoa, trieuChung, chanDoan).
    + 403 Forbidden (User là bệnh nhân nhưng cố tình gọi API tạo ca khám của bác sĩ)

# Testcase (kịch bản kiểm thử) riêng biệt của API 4
# (POST /api/v1/records)
- TC_API4_01 (Happy Path): Gửi Request đầy đủ maBenhNhan, maBacSi, chuyenKhoa, trieuChung, chanDoan, ghiChuDonThuoc. Dùng Token Bác sĩ
->  Kết quả: HTTP 201 Created; Trả về maCaKham tự sinh

- TC_API4_02 (Boundary - Khuyết trường tùy chọn): Gửi Request đầy đủ trường bắt buộc, nhưng bỏ trống ghiChuDonThuoc (truyền chuỗi rỗng "" hoặc null)
->  Kết quả: HTTP 201 Created

- TC_API4_03 (Validation - Thiếu trường bắt buộc): Gửi Request bỏ trống chuyenKhoa, trieuChung hoặc chanDoan. Kết quả: HTTP 400 Bad Request; Báo thiếu trường dữ liệu
->  Kết quả: HTTP 400 Bad Request; Báo thiếu trường dữ liệu

- TC_API4_04 (Validation - Quá giới hạn ký tự): Nhập trường trieuChung mang chuỗi văn bản dài hơn 2000 ký tự (vượt giới hạn bảng MedicalRecords)
->  Kết quả: HTTP 400 Bad Request.

- TC_API4_05 (Security - Phân quyền sai): Dùng JWT Token của Bệnh nhân để cố tình gọi API POST tạo ca khám
->  Kết quả: HTTP 403 Forbidden
-------------------

# API 5 (Tạo mới bệnh nhân - API ẩn - Test Data Setup) Chức năng Tạo bệnh nhân không nằm trong phạm vi giao diện SUT. API này được xây dựng ngầm ở BE đóng vai trò làm công cụ hỗ trợ thiết lập dữ liệu phục vụ riêng cho tiến trình kiểm thử tự động
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
    }
- Response Body & HTTP Status Codes mong đợi:
    + 201 Created (tạo thành công, hệ thống tự sinh maBenhNhan):
        {
            "maBenhNhan": "BN00102",
            "message": "Tạo hồ sơ bệnh nhân thành công"
        }
    + 409 Conflict (trùng số CCCD đã tồn tại trong hệ thống)
    + 400 Bad Request (thiếu trường bắt buộc như họ tên, CCCD)

# Testcase (kịch bản kiểm thử) riêng biệt của API 5
# (POST /api/v1/patients - API Ẩn Set Data)   
- TC_API5_01 (Happy Path): Gửi Request với soCCCD mới tinh và đầy đủ thông tin bắt buộc. 
->  Kết quả: HTTP 201 Created; Trả về maBenhNhan mới

- TC_API5_02 (Negative - Trùng lặp CCCD): Gửi Request chứa soCCCD đã được đăng ký cho một bệnh nhân khác trong cơ sở dữ liệu.
->  Kết quả: HTTP 409 Conflict; Báo lỗi từ chối tạo mới do trùng lặp CCCD.

- TC_API5_03 (Validation - Thiếu trường bắt buộc): Gửi Request bỏ trống hoặc null các trường cốt lõi như soCCCD, hoVaTen hoặc ngaySinh.
->  Kết quả: HTTP 400 Bad Request; Báo lỗi thiếu thông tin bắt buộc.

- TC_API5_04 (Boundary - Tối giản dữ liệu): Gửi Request chỉ điền các trường bắt buộc, hoàn toàn bỏ trống các trường tùy chọn (sdt, diaChi, gioiTinh).
->  Kết quả: HTTP 201 Created; Vẫn tạo thành công và hệ thống tự gán giá trị mặc định cho trường giới tính (nếu cần).

- TC_API5_05 (Validation - Sai định dạng Content-Type): Gửi Request body dưới dạng text/plain hoặc x-www-form-urlencoded thay vì chuẩn application/json.
->  Kết quả: HTTP 415 Unsupported Media Type (hoặc 400); Hệ thống chặn request do sai định dạng.
----------------------            

# API 6 (Lấy danh sách Bác sĩ (bổ trợ UI) - API dùng để fill dữ liệu bác sĩ phụ trách): 
- Endpoint: /api/v1/doctors
- Method: GET
- Query Parameter (tùy chọn): ?chuyenKhoa={ten_khoa} (Dùng để lọc bác sĩ theo text tên khoa nếu cần. Nếu không truyền sẽ trả về toàn bộ danh sách).
- Request Body: không có
- Response Body & HTTP Status Codes mong đợi:
    + 200 OK:
        [
    { 
        "maBacSi": "BS001", 
        "tenBacSi": "Nguyễn Văn A", 
        "chuyenKhoa": "Nội tim mạch" 
    },
    { 
        "maBacSi": "BS002", 
        "tenBacSi": "Lê Thị C", 
        "chuyenKhoa": "Ngoại khoa" 
    }
]

# Testcase (kịch bản kiểm thử) riêng biệt của API 6
# (GET /api/v1/doctors)
- TC_API6_01 (Happy Path - Lấy tất cả): Gửi Request không đính kèm query parameter ?chuyenKhoa=
->  Kết quả: HTTP 200 OK; Trả về mảng JSON chứa toàn bộ danh sách bác sĩ có trong hệ thống.

- TC_API6_02 (Happy Path - Lọc có dữ liệu): Gửi Request đính kèm tham số ?chuyenKhoa=Nội tổng hợp (chuyên khoa có tồn tại bác sĩ trong DB).
->  Kết quả: HTTP 200 OK; Trả về mảng JSON chỉ chứa các bác sĩ thuộc khoa Nội tổng hợp.

- TC_API6_03 (Boundary - Lọc không có dữ liệu): Gửi Request đính kèm tham số ?chuyenKhoa=Nha khoa (chuyên khoa chưa có bác sĩ nào phụ trách).
->  Kết quả: HTTP 200 OK; Trả về một mảng rỗng [].

- TC_API6_04 (Validation - Encoding URL): Gửi Request đính kèm tham số chứa dấu cách hoặc ký tự tiếng Việt đã được mã hóa URL (Ví dụ: ?chuyenKhoa=Nội%20tổng%20hợp).
->  Kết quả: HTTP 200 OK; Backend tự động decode thành công và trả về danh sách bác sĩ tương ứng.

- TC_API6_05 (Security - Sai Method): Cố tình sử dụng phương thức POST hoặc DELETE gọi vào endpoint /api/v1/doctors thay vì GET.
->  Kết quả: HTTP 405 Method Not Allowed; Backend từ chối xử lý do sai thao tác HTTP.
------------------------

# POM
Dự án áp dụng chặt chẽ mẫu thiết kế Page Object Model để tách biệt giao diện và kịch bản test:

#pages/base_page.py: Chứa các hàm tương tác chung (click, fill, wait) dùng chung cho mọi trang.

pages/login_page.py: Đóng gói locator và hành vi của Màn hình 1 (Đăng nhập).

pages/search_page.py: Đóng gói locator của Màn hình 2 (Tra cứu CCCD).

pages/timeline_page.py: Đóng gói locator của Màn hình 3 (Timeline bệnh án).

pages/add_record_page.py: Đóng gói locator của Màn hình 4 (Thêm ca khám mới).

Lưu ý: Nếu UI của SUT thay đổi, chỉ cần cập nhật locator trong thư mục pages/, các file kịch bản trong thư mục tests/e2e/ được giữ nguyên.