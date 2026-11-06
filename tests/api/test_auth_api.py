import pytest
import requests
import allure
import json

# Khai báo URL gốc của Backend
BASE_URL = "https://localhost:7053/api/v1/auth/login"

@allure.epic("API Testing - Medical Record System")
@allure.feature("API Xác Thực (Auth)")
class TestAuthAPI:

    @allure.story("Đăng nhập (Login)")
    @allure.title("TC_API1_01: Kiểm tra đăng nhập luồng Bác sĩ hợp lệ")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.happy_path
    def test_api1_01_login_doctor_success(self):
        payload = {
            "tenDangNhap": "BS_NguyenVanA",
            "matKhau": "Password123!"
        }
        
        with allure.step("Bước 1: Chuẩn bị payload tài khoản Bác sĩ hợp lệ"):
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới endpoint đăng nhập"):
            response = requests.post(BASE_URL, json=payload, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        with allure.step("Bước 4: Kiểm tra response trả về đúng phân quyền và chứa Token"):
            data = response.json()
            assert "token" in data, "Response thiếu JWT Token"
            assert data["vaiTro"] == "Bác sĩ", "Sai phân quyền vai trò"
            assert "maBacSi" in data, "Response thiếu mã định danh Bác sĩ"

    @allure.story("Đăng nhập (Login)")
    @allure.title("TC_API1_02: Kiểm tra đăng nhập luồng Bệnh nhân hợp lệ")
    @pytest.mark.api
    @pytest.mark.happy_path
    def test_api1_02_login_patient_success(self):
        payload = {
            "tenDangNhap": "BN_TranThiB",
            "matKhau": "PatientPass456!"
        }
        
        with allure.step("Bước 1: Chuẩn bị payload tài khoản Bệnh nhân hợp lệ"):
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới endpoint đăng nhập"):
            response = requests.post(BASE_URL, json=payload, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        with allure.step("Bước 4: Kiểm tra response trả về đúng phân quyền và chứa Token"):
            data = response.json()
            assert "token" in data, "Response thiếu JWT Token"
            assert data["vaiTro"] == "Bệnh nhân", "Sai phân quyền vai trò"
            assert "maBenhNhan" in data, "Response thiếu mã định danh Bệnh nhân"

    @allure.story("Đăng nhập (Login)")
    @allure.title("TC_API1_03: Kiểm tra đăng nhập đúng username nhưng sai password")
    @pytest.mark.api
    @pytest.mark.error_path
    def test_api1_03_login_wrong_password(self):
        payload = {
            "tenDangNhap": "BS_NguyenVanA",
            "matKhau": "SaiMatKhau!!!"
        }
        
        with allure.step("Bước 1: Chuẩn bị payload tài khoản đúng, mật khẩu sai"):
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới endpoint đăng nhập"):
            response = requests.post(BASE_URL, json=payload, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra HTTP Status Code (Nhận được: {response.status_code}) - Mong đợi 401"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 401, f"Expected 401, got {response.status_code}"
            
        with allure.step("Bước 4: Kiểm tra thông báo lỗi trả về"):
            assert "Sai tài khoản hoặc mật khẩu" in response.text, "Thông báo lỗi không khớp"

    @allure.story("Đăng nhập (Login)")
    @allure.title("TC_API1_04: Kiểm tra gửi request bỏ trống dữ liệu")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api1_04_login_empty_data(self):
        payload = {
            "tenDangNhap": "",
            "matKhau": ""
        }
        
        with allure.step("Bước 1: Chuẩn bị payload rỗng các trường bắt buộc"):
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới endpoint đăng nhập"):
            response = requests.post(BASE_URL, json=payload, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra API bắt lỗi 400 Bad Request (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @allure.story("Đăng nhập (Login)")
    @allure.title("TC_API1_05: Kiểm tra gửi body dạng plain text thay vì JSON")
    @pytest.mark.api
    @pytest.mark.error_path
    def test_api1_05_login_invalid_format(self):
        payload_text = "tenDangNhap=BS_NguyenVanA&matKhau=123"
        headers = {'Content-Type': 'text/plain'}
        
        with allure.step("Bước 1: Chuẩn bị payload dạng chuỗi văn bản (Plain Text)"):
            allure.attach(payload_text, name="Request Text Payload", attachment_type=allure.attachment_type.TEXT)
            
        with allure.step("Bước 2: Gửi request POST kèm header Content-Type: text/plain"):
            response = requests.post(BASE_URL, data=payload_text, headers=headers, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra server từ chối format không hợp lệ (Mã 400 hoặc 415) (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code in [400, 415], f"Expected 400 or 415, got {response.status_code}"