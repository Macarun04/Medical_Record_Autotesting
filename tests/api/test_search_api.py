import pytest
import requests
import allure
import json

BASE_URL = "https://localhost:7053/api/v1/patients/search"

@allure.epic("API Testing - Medical Record System")
@allure.feature("API Tìm Kiếm CCCD (Search)")
class TestSearchAPI:

    @allure.story("Tra cứu CCCD")
    @allure.title("TC_API2_01: Tra cứu CCCD hợp lệ có trong DB")
    @pytest.mark.api
    @pytest.mark.happy_path
    def test_api2_01_search_valid_cccd(self, doctor_headers):
        with allure.step("Bước 1: Gửi request GET tra cứu CCCD hợp lệ (012345678912)"):
            response = requests.get(f"{BASE_URL}?cccd=012345678912", headers=doctor_headers, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200
            
        with allure.step("Bước 3: Xác minh dữ liệu trả về đúng với CCCD cần tra cứu"):
            data = response.json()
            assert data["soCCCD"] == "012345678912"
            assert "maBenhNhan" in data

    @allure.story("Tra cứu CCCD")
    @allure.title("TC_API2_02: CCCD đúng định dạng 12 số nhưng không tồn tại")
    @pytest.mark.api
    @pytest.mark.error_path
    def test_api2_02_search_not_found(self, doctor_headers):
        with allure.step("Bước 1: Gửi request GET tra cứu CCCD không có thật trong DB"):
            response = requests.get(f"{BASE_URL}?cccd=999999999999", headers=doctor_headers, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra API báo lỗi 404 Not Found (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 404
            assert "Không tìm thấy" in response.text 

    @allure.story("Tra cứu CCCD")
    @allure.title("TC_API2_03: CCCD sai độ dài (9 hoặc 13 số thay vì 12 số)")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api2_03_search_invalid_length(self, doctor_headers):
        with allure.step("Bước 1: Gửi request GET tra cứu CCCD sai độ dài (9 số)"):
            response = requests.get(f"{BASE_URL}?cccd=123456789", headers=doctor_headers, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra API chặn Validation báo lỗi 400 (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 400

    @allure.story("Tra cứu CCCD")
    @allure.title("TC_API2_04: CCCD chứa ký tự lạ/chữ cái")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api2_04_search_special_chars(self, doctor_headers):
        with allure.step("Bước 1: Gửi request GET tra cứu CCCD chứa chữ cái"):
            response = requests.get(f"{BASE_URL}?cccd=01234567891a", headers=doctor_headers, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra API chặn Validation báo lỗi 400 (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 400

    @allure.story("Tra cứu CCCD")
    @allure.title("TC_API2_05: Không truyền tham số cccd trên URL")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api2_05_search_missing_param(self, doctor_headers):
        with allure.step("Bước 1: Gửi request GET nhưng thiếu hoàn toàn query param cccd"):
            response = requests.get(BASE_URL, headers=doctor_headers, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra API bắt buộc tham số và báo lỗi 400 (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 400