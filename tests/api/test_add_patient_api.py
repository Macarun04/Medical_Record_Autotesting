import pytest
import requests
import allure
import json

BASE_URL = "https://localhost:7053/api/v1/patients"

@allure.epic("API Testing - Medical Record System")
@allure.feature("API Bệnh Nhân (Patients)")
class TestAddPatientAPI:

    @allure.story("Thêm mới bệnh nhân (POST)")
    @allure.title("TC_API5_01: Tạo hồ sơ bệnh nhân mới đầy đủ thông tin bằng Faker")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.happy_path
    def test_api5_01_create_patient_success(self, fake_patient_data):
        with allure.step(f"Bước 1: Chuẩn bị payload dữ liệu Bệnh nhân: {fake_patient_data.get('hoVaTen', 'N/A')}"):
            # Đính kèm dữ liệu gửi đi vào report
            allure.attach(json.dumps(fake_patient_data, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
            
        with allure.step("Bước 2: Gửi request POST tới server"):
            response = requests.post(BASE_URL, json=fake_patient_data, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 201, f"Expected 201, got {response.status_code}"
            
        with allure.step("Bước 4: Kiểm tra dữ liệu JSON trả về phải tự động sinh maBenhNhan"):
            data = response.json()
            assert "maBenhNhan" in data or "maBenhNhan" in data.get("data", {}), "Phải tự động sinh maBenhNhan"

    @allure.story("Thêm mới bệnh nhân (POST)")
    @allure.title("TC_API5_02: Trùng lặp số CCCD đã tồn tại trong DB")
    @pytest.mark.api
    @pytest.mark.error_path
    def test_api5_02_create_patient_duplicate(self, fake_patient_data):
        with allure.step("Bước 1: Đẩy cục data ngẫu nhiên vào DB lần 1 (Thành công 201)"):
            requests.post(BASE_URL, json=fake_patient_data, verify=False)
            allure.attach(json.dumps(fake_patient_data, ensure_ascii=False, indent=2), name="Request Payload (Dùng chung cho cả 2 lần gọi)", attachment_type=allure.attachment_type.JSON)
        
        with allure.step("Bước 2: Gửi y hệt cục data cũ (trùng CCCD) vào DB lần 2"):
            response = requests.post(BASE_URL, json=fake_patient_data, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra C# phải chặn lại với Status Code 409 Conflict (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 409, f"Expected 409 Conflict, got {response.status_code}"

    @allure.story("Thêm mới bệnh nhân (POST)")
    @allure.title("TC_API5_03: Bỏ trống trường bắt buộc (Xóa hoVaTen và ngaySinh)")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api5_03_create_patient_missing_req(self, fake_patient_data):
        with allure.step("Bước 1: Lấy data ngẫu nhiên, cố tình xóa đi 2 trường bắt buộc (hoVaTen, ngaySinh)"):
            del fake_patient_data["hoVaTen"]
            del fake_patient_data["ngaySinh"]
            allure.attach(json.dumps(fake_patient_data, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
        
        with allure.step("Bước 2: Gửi request POST tới server"):
            response = requests.post(BASE_URL, json=fake_patient_data, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra API bắt được lỗi 400 Bad Request do thiếu trường (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 400, "Phải bắt được lỗi 400 Bad Request do thiếu trường"

    @allure.story("Thêm mới bệnh nhân (POST)")
    @allure.title("TC_API5_04: Cố tình nhập thiếu SĐT và Địa chỉ khi DB đã yêu cầu NOT NULL")
    @pytest.mark.api
    @pytest.mark.error_path
    def test_api5_04_create_patient_min_data(self, fake_patient_data):
        with allure.step("Bước 1: Lấy data ngẫu nhiên, cố tình xóa SĐT, Địa chỉ và BHYT"):
            del fake_patient_data["sdt"]
            del fake_patient_data["diaChi"]
            del fake_patient_data["doiTuongBHYT"]
            allure.attach(json.dumps(fake_patient_data, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
        
        with allure.step("Bước 2: Gửi request POST tới server"):
            response = requests.post(BASE_URL, json=fake_patient_data, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra API chặn lại với lỗi 400 Bad Request (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 400, f"Expected 400, got {response.status_code}. API phải chặn lại do thiếu SDT và DiaChi!"

    @allure.story("Thêm mới bệnh nhân (POST)")
    @allure.title("TC_API5_05: Sai định dạng DateTime (Nhập ngày 32/13)")
    @pytest.mark.api
    @pytest.mark.error_path
    def test_api5_05_create_patient_bad_date(self, fake_patient_data):
        with allure.step("Bước 1: Ghi đè ngày sinh ngẫu nhiên bằng một ngày sai logic (32/13/1990)"):
            fake_patient_data["ngaySinh"] = "32/13/1990" 
            allure.attach(json.dumps(fake_patient_data, ensure_ascii=False, indent=2), name="Request Payload", attachment_type=allure.attachment_type.JSON)
        
        with allure.step("Bước 2: Gửi request POST tới server"):
            response = requests.post(BASE_URL, json=fake_patient_data, verify=False)
        
        with allure.step(f"Bước 3: Kiểm tra ASP.NET Core tự động chặn ngày tháng không hợp lệ (400) (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 400, "ASP.NET Core phải tự động chặn ngày tháng không hợp lệ (400)"