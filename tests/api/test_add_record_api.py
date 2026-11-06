import pytest
import requests
import allure
import json

BASE_URL = "https://localhost:7053/api/v1/records"

# Token giả lập phục vụ cho các test case phân quyền
HEADERS_DOCTOR = {"Authorization": "Bearer BearerToken_Doctor_Valid"}
HEADERS_PATIENT = {"Authorization": "Bearer BearerToken_Patient_BN01"}


@allure.epic("API Testing - Medical Record System")
@allure.feature("API Ca Khám (Records)")
class TestAddRecordAPI:

    @allure.story("Thêm mới ca khám (POST)")
    @allure.title("TC_API4_01: Tạo ca khám đầy đủ thông tin (Token Bác sĩ)")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.happy_path
    def test_api4_01_create_record_success(self):
        payload = {
            "maBenhNhan": "BN_01",
            "maBacSi": "BS_01",
            "trieuChung": "Ho khan, sốt nhẹ",
            "chanDoan": "Viêm họng cấp",
            "ghiChuDonThuoc": "Kháng sinh 5 ngày, tái khám sau 1 tuần"
        }
        
        with allure.step("Bước 1: Chuẩn bị payload dữ liệu Ca khám đầy đủ"):
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới server bằng Token Bác sĩ"):
            response = requests.post(BASE_URL, json=payload, headers=HEADERS_DOCTOR, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 201, f"Expected 201, got {response.status_code}"
            
        with allure.step("Bước 4: Kiểm tra dữ liệu JSON trả về phải tự động sinh maCaKham"):
            data = response.json()
            assert "maCaKham" in data.get("data", {}) or "maCaKham" in data, "Phải trả về mã ca khám"

    @allure.story("Thêm mới ca khám (POST)")
    @allure.title("TC_API4_02: Tạo ca khám thiếu trường tùy chọn (ghiChuDonThuoc để trống/null)")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api4_02_create_record_opt_field(self):
        payload = {
            "maBenhNhan": "BN_01",
            "maBacSi": "BS_01",
            "trieuChung": "Đau đầu chóng mặt",
            "chanDoan": "Thiếu máu não",
            "ghiChuDonThuoc": None # Bỏ trống tùy chọn theo đúng ma trận
        }
        
        with allure.step("Bước 1: Chuẩn bị payload thiếu trường tùy chọn (ghiChuDonThuoc = None)"):
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới server"):
            response = requests.post(BASE_URL, json=payload, headers=HEADERS_DOCTOR, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra HTTP Status Code vẫn phải là 201 Created (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    @allure.story("Thêm mới ca khám (POST)")
    @allure.title("TC_API4_03: Bỏ trống các trường bắt buộc (để trống chanDoan)")
    @pytest.mark.api
    @pytest.mark.error_path
    def test_api4_03_create_record_missing(self):
        payload = {
            "maBenhNhan": "BN_01",
            "maBacSi": "BS_01",
            "trieuChung": "Sốt cao",
            "chanDoan": "" # Cố tình để trống trường chẩn đoán
        }
        
        with allure.step("Bước 1: Chuẩn bị payload cố tình để trống trường bắt buộc (chanDoan rỗng)"):
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới server"):
            response = requests.post(BASE_URL, json=payload, headers=HEADERS_DOCTOR, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra API bắt được lỗi 400 Bad Request (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 400, "Phải trả về 400 Bad Request do thiếu trường bắt buộc"

    @allure.story("Thêm mới ca khám (POST)")
    @allure.title("TC_API4_04: Vượt giới hạn ký tự DB (Trường trieuChung dài 2001 ký tự)")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api4_04_create_record_max_len(self):
        payload = {
            "maBenhNhan": "BN_01",
            "maBacSi": "BS_01",
            "trieuChung": "A" * 2001, # Cố tình tạo chuỗi dài 2001 ký tự vượt ngưỡng 2000
            "chanDoan": "Kiểm tra giới hạn ký tự"
        }
        
        with allure.step("Bước 1: Chuẩn bị payload với chuỗi trieuChung vượt quá 2000 ký tự"):
            # Lấy 100 ký tự đầu để gắn vào report tránh quá dài
            snippet = payload.copy()
            snippet["trieuChung"] = snippet["trieuChung"][:100] + "... [TRUNCATED for Log]"
            allure.attach(json.dumps(snippet, ensure_ascii=False, indent=2), name="Request Payload (Snippet)", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới server"):
            response = requests.post(BASE_URL, json=payload, headers=HEADERS_DOCTOR, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra C# chặn lại và báo lỗi 400 Bad Request (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 400, "Phải báo 400 Bad Request khi vượt quá giới hạn ký tự"

    @allure.story("Bảo mật & Phân quyền Ca khám")
    @allure.title("TC_API4_05: Phân quyền sai vai trò (Dùng Token Bệnh nhân gọi POST)")
    @pytest.mark.api
    @pytest.mark.error_path
    @pytest.mark.security
    def test_api4_05_create_record_wrong_role(self):
        payload = {
            "maBenhNhan": "BN_01",
            "maBacSi": "BS_01",
            "trieuChung": "Đau bụng",
            "chanDoan": "Đau dạ dày"
        }
        
        with allure.step("Bước 1: Chuẩn bị payload và Token xác thực của Bệnh nhân (BN01)"):
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới server bằng quyền Bệnh nhân"):
            response = requests.post(BASE_URL, json=payload, headers=HEADERS_PATIENT, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra hệ thống chặn lỗi 403 Forbidden (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 403, "Phải trả về 403 Forbidden do sai phân quyền"