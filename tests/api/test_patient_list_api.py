import pytest
import requests
import allure
import json

BASE_URL = "https://localhost:7053/api/v1/patients"
HEADERS_DOCTOR = {"Authorization": "Bearer BearerToken_Doctor_Valid"}
HEADERS_PATIENT = {"Authorization": "Bearer BearerToken_Patient_BN01"}

@allure.epic("API Testing - Medical Record System")
@allure.feature("API Bệnh Nhân (Patients)")
class TestPatientListAPI:

    @allure.story("Lấy danh sách Bệnh nhân (GET)")
    @allure.title("TC_API8_01: Lấy toàn bộ danh sách bệnh nhân thành công (Token Bác sĩ)")
    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.happy_path
    def test_api8_01_get_patients_success(self):
        with allure.step("Bước 1: Gửi request GET tới server bằng Token Bác sĩ"):
            response = requests.get(BASE_URL, headers=HEADERS_DOCTOR, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
        with allure.step("Bước 3: Kiểm tra cấu trúc response chứa danh sách mảng (list)"):
            data = response.json()
            assert isinstance(data, list) or isinstance(data.get("data"), list), "Response phải chứa danh sách bệnh nhân"

    @allure.story("Lấy danh sách Bệnh nhân (GET)")
    @allure.title("TC_API8_02: Lọc danh sách trả về mảng rỗng khi điều kiện tìm kiếm không khớp")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api8_02_get_patients_empty(self):
        with allure.step("Bước 1: Gửi request GET kèm query search không tồn tại"):
            response = requests.get(f"{BASE_URL}?search=KhongCoAiTonTaiTrongNay12345", headers=HEADERS_DOCTOR, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra HTTP Status Code (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
        with allure.step("Bước 3: Kiểm tra kết quả trả về là mảng rỗng do không khớp dữ liệu"):
            data = response.json()
            result_list = data if isinstance(data, list) else data.get("data", [])
            assert len(result_list) == 0, "Kết quả tìm kiếm không khớp phải trả về mảng rỗng []"

    @allure.story("Lấy danh sách Bệnh nhân (GET)")
    @allure.title("TC_API8_03: Kiểm thử biên với tham số phân trang sai định dạng")
    @pytest.mark.api
    @pytest.mark.boundary
    def test_api8_03_get_patients_invalid_param(self):
        with allure.step("Bước 1: Gửi request GET kèm tham số phân trang sai (page âm, pageSize chứa chữ)"):
            response = requests.get(f"{BASE_URL}?page=-1&pageSize=abc", headers=HEADERS_DOCTOR, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra server xử lý an toàn (400 hoặc fallback 200) (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code in [200, 400], f"Expected 400 or fallback 200, got {response.status_code}"

    @allure.story("Bảo mật & Phân quyền Bệnh nhân")
    @allure.title("TC_API8_04: Phân quyền truy cập sai vai trò (Dùng Token Bệnh nhân gọi GET toàn bộ)")
    @pytest.mark.api
    @pytest.mark.error_path
    @pytest.mark.security
    def test_api8_04_get_patients_wrong_role(self):
        with allure.step("Bước 1: Gửi request GET lấy danh sách toàn viện nhưng dùng Token Bệnh nhân"):
            response = requests.get(BASE_URL, headers=HEADERS_PATIENT, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra server chặn quyền 403 Forbidden (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"

    @allure.story("Bảo mật & Phân quyền Bệnh nhân")
    @allure.title("TC_API8_05: Block truy cập không ủy quyền vào danh sách bệnh nhân (Không Token)")
    @pytest.mark.api
    @pytest.mark.error_path
    @pytest.mark.security
    def test_api8_05_get_patients_no_auth(self):
        with allure.step("Bước 1: Gửi request GET hoàn toàn KHÔNG có header Authorization"):
            response = requests.get(BASE_URL, verify=False)
        
        with allure.step(f"Bước 2: Kiểm tra server chặn lại với lỗi 401 Unauthorized (Nhận được: {response.status_code})"):
            allure.attach(response.text, name="Response Body", attachment_type=allure.attachment_type.JSON)
            assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"