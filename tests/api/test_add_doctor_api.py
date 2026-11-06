import pytest
import requests
import allure
import json

BASE_URL = "https://localhost:7053/api/v1/doctors"

# Các token giả lập phân quyền cho phân hệ tạo bác sĩ
HEADERS_ADMIN = {"Authorization": "Bearer BearerToken_Admin_Valid"}
HEADERS_DOCTOR = {"Authorization": "Bearer BearerToken_Doctor_Valid"}
HEADERS_PATIENT = {"Authorization": "Bearer BearerToken_Patient_BN01"}

@allure.epic("API Testing - Medical Record System")
@allure.feature("API Bác Sĩ (Doctors)")
class TestAddDoctorAPI:

    @allure.story("Thêm mới bác sĩ (POST)")
    @allure.title("TC_API7_01: Tạo hồ sơ bác sĩ mới thành công với dữ liệu động")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.happy_path
    def test_api7_01_create_doctor_success(self, fake_doctor_data):
        with allure.step(f"Bước 1: Chuẩn bị payload dữ liệu Bác sĩ: {fake_doctor_data['tenBacSi']}"):
            # Đính kèm payload vào report để dễ trace lỗi
            allure.attach(json.dumps(fake_doctor_data, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới server với quyền Admin"):
            response = requests.post(BASE_URL, json=fake_doctor_data, headers=HEADERS_ADMIN, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
            
        with allure.step("Bước 4: Kiểm tra dữ liệu JSON trả về phải chứa maBacSi"):
            data = response.json()
            assert "maBacSi" in data.get("data", {}) or "maBacSi" in data

    @allure.story("Thêm mới bác sĩ (POST)")
    @allure.title("TC_API7_02: Trùng lặp mã bác sĩ đã tồn tại trong DB")
    @pytest.mark.api
    @pytest.mark.error_path
    def test_api7_02_create_doctor_duplicate(self):
        payload = {
            "maBacSi": "BS_01", # Giả sử BS_01 đã tồn tại sẵn trong DB
            "tenBacSi": "Bác sĩ trùng",
            "chuyenKhoa": "Ngoại khoa"
        }
        with allure.step("Bước 1: Chuẩn bị payload trùng mã bác sĩ BS_01"):
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)

        with allure.step("Bước 2: Gửi request POST tới server"):
            response = requests.post(BASE_URL, json=payload, headers=HEADERS_ADMIN, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra Status Code phải là 409 Conflict (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 409, f"Expected 409 Conflict, got {response.status_code}"

    @allure.story("Thêm mới bác sĩ (POST)")
    @allure.title("TC_API7_03: Bỏ trống các trường NOT NULL bắt buộc")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api7_03_create_doctor_missing_req(self):
        payload = {
            "maBacSi": "BS_NEW_02",
            "tenBacSi": "", # Cố tình để trống trường bắt buộc
            "chuyenKhoa": ""
        }
        with allure.step("Bước 1: Chuẩn bị payload thiếu dữ liệu bắt buộc (Tên và Chuyên khoa rỗng)"):
            allure.attach(json.dumps(payload, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
        
        with allure.step("Bước 2: Gửi request POST tới server"):
            response = requests.post(BASE_URL, json=payload, headers=HEADERS_ADMIN, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra Status Code phải là 400 Bad Request (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 400, "Phải trả về 400 Bad Request khi thiếu trường bắt buộc"

    @allure.story("Bảo mật & Phân quyền Bác sĩ")
    @allure.title("TC_API7_04: Phân quyền sai vai trò (Dùng Token Bác sĩ thường)")
    @pytest.mark.api
    @pytest.mark.error_path
    @pytest.mark.security
    def test_api7_04_create_doctor_wrong_role(self):
        payload = {
            "maBacSi": "BS_NEW_03",
            "tenBacSi": "Lỗi phân quyền",
            "chuyenKhoa": "Nhi khoa"
        }
        with allure.step("Bước 1: Gửi request POST với Token của Bác sĩ thường (Không phải Admin)"):
            response = requests.post(BASE_URL, json=payload, headers=HEADERS_DOCTOR, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra Status Code phải bị chặn lỗi 403 Forbidden (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"

    @allure.story("Bảo mật & Phân quyền Bác sĩ")
    @allure.title("TC_API7_05: Block truy cập không ủy quyền (Không truyền Token)")
    @pytest.mark.api
    @pytest.mark.error_path
    @pytest.mark.security
    def test_api7_05_create_doctor_no_auth(self):
        payload = {
            "maBacSi": "BS_NEW_04",
            "tenBacSi": "Không token",
            "chuyenKhoa": "Da liễu"
        }
        with allure.step("Bước 1: Gửi request POST hoàn toàn KHÔNG có header Authorization"):
            response = requests.post(BASE_URL, json=payload, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra Status Code phải bị chặn lỗi 401 Unauthorized (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"