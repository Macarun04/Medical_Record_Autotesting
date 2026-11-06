import pytest
import requests
import allure
import json

BASE_URL = "https://localhost:7053/api/v1/doctors"
HEADERS_VALID = {"Authorization": "Bearer BearerToken_Doctor_Valid"}

@allure.epic("API Testing - Medical Record System")
@allure.feature("API Bác Sĩ (Doctors)")
class TestDoctorListAPI:

    @allure.story("Lấy danh sách Bác sĩ (GET)")
    @allure.title("TC_API6_01_Doctors_GetAll: Lấy toàn bộ danh sách bác sĩ không truyền query param")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.happy_path
    def test_api6_01_doctors_get_all(self):
        with allure.step("Bước 1: Gửi request GET tới server"):
            response = requests.get(BASE_URL, headers=HEADERS_VALID, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
        with allure.step("Bước 3: Kiểm tra cấu trúc dữ liệu trả về (phải là list chứa maBacSi)"):
            data = response.json()
            assert isinstance(data, list), "Response phải là một mảng danh sách"
            if len(data) > 0:
                assert "maBacSi" in data[0], "Mỗi object bác sĩ phải có trường maBacSi"

    @allure.story("Lấy danh sách Bác sĩ (GET)")
    @allure.title("TC_API6_02_Doctors_FilterExist: Lọc theo chuyên khoa đang có dữ liệu (Nội khoa)")
    @pytest.mark.api
    @pytest.mark.happy_path
    def test_api6_02_doctors_filter_exist(self):
        with allure.step("Bước 1: Gửi request GET kèm query param ?chuyenKhoa=Nội khoa"):
            response = requests.get(f"{BASE_URL}?chuyenKhoa=Nội khoa", headers=HEADERS_VALID, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
        with allure.step("Bước 3: Xác minh toàn bộ bác sĩ trả về đều thuộc Nội khoa"):
            data = response.json()
            assert isinstance(data, list)
            for doctor in data:
                assert doctor["chuyenKhoa"] == "Nội khoa", "Tất cả bác sĩ trả về phải thuộc khoa Nội khoa"

    @allure.story("Lấy danh sách Bác sĩ (GET)")
    @allure.title("TC_API6_03_Doctors_FilterEmpty: Lọc theo khoa chưa có người (Nha khoa)")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api6_03_doctors_filter_empty(self):
        with allure.step("Bước 1: Gửi request GET kèm query param chuyên khoa lạ (?chuyenKhoa=Nha khoa)"):
            response = requests.get(f"{BASE_URL}?chuyenKhoa=Nha khoa", headers=HEADERS_VALID, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
        with allure.step("Bước 3: Kiểm tra hệ thống trả về mảng rỗng [] thay vì báo lỗi"):
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0, "Khoa chưa có data phải trả về mảng rỗng []"

    @allure.story("Lấy danh sách Bác sĩ (GET)")
    @allure.title("TC_API6_04_Doctors_Encoding: Truyền ký tự mã hóa URL/UTF-8 (?chuyenKhoa=Nội%20khoa)")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api6_04_doctors_encoding(self):
        with allure.step("Bước 1: Gửi request GET với query param chứa khoảng trắng đã encode URL"):
            response = requests.get(f"{BASE_URL}?chuyenKhoa=Nội%20khoa", headers=HEADERS_VALID, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
        with allure.step("Bước 3: Xác minh server tự decode URL và trả về đúng dữ liệu Nội khoa"):
            data = response.json()
            assert isinstance(data, list)
            for doctor in data:
                assert doctor["chuyenKhoa"] == "Nội khoa"

    @allure.story("Bảo mật & Phân quyền Bác sĩ")
    @allure.title("TC_API6_05_Doctors_NoAuth: Block truy cập không ủy quyền (Không truyền Token)")
    @pytest.mark.api
    @pytest.mark.error_path
    @pytest.mark.security
    def test_api6_05_doctors_no_auth(self):
        with allure.step("Bước 1: Gửi request GET nhưng cố tình KHÔNG đính kèm header Authorization"):
            response = requests.get(BASE_URL, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra cơ chế bảo mật chặn lại với mã 401 (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"