# Bảng Chốt Phạm Vi Kiểm Thử (Scope Freeze)

- **Dự án:** Hệ thống Kiểm thử Tự động Quản lý Hồ sơ Bệnh án (Medical Record Autotesting)
- **Tổng phạm vi chốt:** 4 màn hình + 8 API = **50 Test Case** (40 API + 10 E2E) ánh xạ tới **21 Yêu cầu (REQ_01 -> REQ_21)**.
- **Nguyên tắc:** Không thêm/bớt test case trong suốt quá trình đo 20 run CI, branch coverage và thí nghiệm cấy 12 defect.

| Thành phần SUT | Phạm vi chốt (Scope Freeze) | Số lượng | Mã Test Case tương ứng |
| :--- | :--- | :---: | :--- |
| **Màn hình 1: Đăng nhập (login.html)** | Đăng nhập Bác sĩ/Bệnh nhân, bắt lỗi sai mật khẩu, validate bỏ trống trường | 4 E2E | TC_UI_01 -> TC_UI_04 |
| **Màn hình 2: Tra cứu Bệnh nhân (search.html)** | Bác sĩ tìm hồ sơ theo CCCD (tồn tại / không tồn tại) | 2 E2E | TC_UI_05 -> TC_UI_06 |
| **Màn hình 3: Lịch sử Khám (	imeline.html)** | Bác sĩ xem lịch sử ca khám; Bệnh nhân xem đúng timeline cá nhân | 2 E2E | TC_UI_07, TC_UI_10 |
| **Màn hình 4: Thêm Ca Khám (Modal/Form)** | Validate thiếu triệu chứng/chẩn đoán; tạo mới và cập nhật timeline | 2 E2E | TC_UI_08 -> TC_UI_09 |
| **API 1: Đăng nhập (POST /api/v1/auth/login)** | Happy path (BS/BN), sai mật khẩu, body rỗng, sai định dạng | 5 API | TC_API1_01 -> TC_API1_05 |
| **API 2: Tra cứu CCCD (GET /api/v1/patients/search)** | Tìm thấy, không thấy (404), sai độ dài, ký tự lạ, thiếu param | 5 API | TC_API2_01 -> TC_API2_05 |
| **API 3: Lấy Timeline (GET /api/v1/medical-records/{id})** | Có dữ liệu, mảng rỗng, không tồn tại, không Token, SQLi | 5 API | TC_API3_01 -> TC_API3_05 |
| **API 4: Thêm Ca Khám (POST /api/v1/medical-records)** | Đủ trường, thiếu trường tùy chọn, thiếu trường bắt buộc, >2000 ký tự, sai quyền | 5 API | TC_API4_01 -> TC_API4_05 |
| **API 5: Tạo Bệnh Nhân (POST /api/v1/patients)** | Tạo mới, trùng CCCD (409), thiếu NOT NULL chính, thiếu trường NOT NULL phụ, sai ngày sinh | 5 API | TC_API5_01 -> TC_API5_05 |
| **API 6: Danh sách Bác Sĩ (GET /api/v1/doctors)** | Lấy tất cả, lọc khoa có/không data, UTF-8 encoding, không Token | 5 API | TC_API6_01 -> TC_API6_05 |
| **API 7: Tạo Bác Sĩ (POST /api/v1/doctors)** | Tạo mới (Admin), trùng mã (409), thiếu trường, sai quyền (403), không Token | 5 API | TC_API7_01 -> TC_API7_05 |
| **API 8: Danh sách Bệnh Nhân (GET /api/v1/patients)** | Lấy danh sách, lọc rỗng, sai tham số phân trang, sai quyền (403), không Token | 5 API | TC_API8_01 -> TC_API8_05 |
| **TỔNG CỘNG PHẠM VI** | **4 Màn hình + 8 API** | **50 Test** | **21 REQ (REQ_01 -> REQ_21)** |