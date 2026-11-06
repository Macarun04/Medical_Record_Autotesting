import pytest
import requests
import allure
import json

BASE_URL = "https://localhost:7053/api/v1/patients"

@allure.epic("API Testing - Medical Record System")
@allure.feature("API Lịch sử khám (Timeline)")
class TestTimelineAPI:

    @allure.story("Xem Lịch sử khám (GET)")
    @allure.title("TC_API3_01: Lấy timeline khi bệnh nhân đã có ca khám")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.happy_path
    def test_api3_01_timeline_has_data(self, doctor_headers):
        ma_benh_nhan = "BN_01" 
        
        with allure.step(f"Bước 1: Gửi request GET lấy timeline của bệnh nhân {ma_benh_nhan}"):
            response = requests.get(f"{BASE_URL}/{ma_benh_nhan}/record", headers=doctor_headers, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
        with allure.step("Bước 3: Xác minh dữ liệu trả về gồm thông tin patient và mảng records"):
            data = response.json()
            assert "patient" in data, "Response thiếu thông tin patient"
            assert "records" in data, "Response thiếu danh sách records"
            assert isinstance(data["records"], list), "records phải là một mảng (list)"

    @allure.story("Xem Lịch sử khám (GET)")
    @allure.title("TC_API3_02: Lấy timeline của bệnh nhân mới tạo (chưa từng khám)")
    @pytest.mark.api
    @pytest.mark.happy_path
    @pytest.mark.boundary
    def test_api3_02_timeline_empty(self, doctor_headers):
        ma_benh_nhan = "BN_03"
        
        with allure.step(f"Bước 1: Gửi request GET lấy timeline của bệnh nhân chưa khám {ma_benh_nhan}"):
            response = requests.get(f"{BASE_URL}/{ma_benh_nhan}/record", headers=doctor_headers, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200
            
        with allure.step("Bước 3: Xác minh hệ thống trả về mảng records rỗng []"):
            data = response.json()
            assert "records" in data
            assert len(data["records"]) == 0, "Bệnh nhân chưa khám phải trả về danh sách records rỗng []"

    @allure.story("Xem Lịch sử khám (GET)")
    @allure.title("TC_API3_03: Truyền sai mã định danh (bệnh nhân không tồn tại)")
    @pytest.mark.api
    @pytest.mark.error_path
    def test_api3_03_timeline_not_found(self, doctor_headers):
        ma_benh_nhan = "ID_KHONG_TON_TAI"
        
        with allure.step(f"Bước 1: Gửi request GET với mã bệnh nhân lạ ({ma_benh_nhan})"):
            response = requests.get(f"{BASE_URL}/{ma_benh_nhan}/record", headers=doctor_headers, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra hệ thống báo lỗi 404 Not Found (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 404, "Phải báo lỗi 404 Not Found"

    @allure.story("Bảo mật & Phân quyền Timeline")
    @allure.title("TC_API3_04: Gọi API nhưng không đính kèm Token (Block truy cập)")
    @pytest.mark.api
    @pytest.mark.error_path
    @pytest.mark.security
    def test_api3_04_timeline_no_auth(self):
        ma_benh_nhan = "BN_01"
        
        with allure.step("Bước 1: Gửi request GET nhưng KHÔNG truyền header Authorization"):
            response = requests.get(f"{BASE_URL}/{ma_benh_nhan}/record", verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra hệ thống chặn 401 Unauthorized (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 401, f"Hệ thống phải chặn và báo 401, nhưng lại trả về {response.status_code}"

    @allure.story("Bảo mật & Phân quyền Timeline")
    @allure.title("TC_API3_05: Kiểm thử bảo mật chặn SQL Injection trên URL")
    @pytest.mark.api
    @pytest.mark.boundary
    @pytest.mark.security
    def test_api3_05_timeline_sqli(self, doctor_headers):
        ma_benh_nhan = "BN_01' OR '1'='1"
        
        with allure.step("Bước 1: Gửi request GET với mã bệnh nhân chứa script SQL Injection"):
            response = requests.get(f"{BASE_URL}/{ma_benh_nhan}/record", headers=doctor_headers, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra ORM chặn SQLi an toàn (404 hoặc 400) (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code in [400, 404], f"Hệ thống không an toàn nếu trả về {response.status_code}"