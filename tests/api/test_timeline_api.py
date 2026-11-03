import pytest
import requests

# Khai báo đúng tên biến HEADERS (viết hoa toàn bộ theo đúng khai báo)
HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.MockTokenForTesting"
}

@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.happy_path
def test_api3_01_timeline_has_data():
    """TC_API3_01: Lấy timeline khi bệnh nhân đã có ca khám"""
    ma_benh_nhan = "BN_01" # Khớp với dữ liệu thực tế trong DB của bạn
    base_url = "https://localhost:7053/api/v1/patients"
    
    response = requests.get(f"{base_url}/{ma_benh_nhan}/record", headers=HEADERS, verify=False)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    # Controller của bạn trả về object chứa 'patient' và 'records'
    assert "patient" in data, "Response thiếu thông tin patient"
    assert "records" in data, "Response thiếu danh sách records"
    assert isinstance(data["records"], list), "records phải là một mảng (list)"

@pytest.mark.api
@pytest.mark.happy_path
@pytest.mark.boundary
def test_api3_02_timeline_empty():
    """TC_API3_02: Lấy timeline của bệnh nhân mới tạo (chưa từng khám)"""
    ma_benh_nhan = "BN_091250" # Lấy BN_091250 trong DB của bạn (đang chưa có ca khám)
    base_url = "https://localhost:7053/api/v1/patients"
    
    response = requests.get(f"{base_url}/{ma_benh_nhan}/record", headers=HEADERS, verify=False)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "records" in data
    assert len(data["records"]) == 0, "Bệnh nhân chưa khám phải trả về danh sách records rỗng []"

@pytest.mark.api
@pytest.mark.error_path
def test_api3_03_timeline_not_found():
    """TC_API3_03: Truyền sai mã định danh (bệnh nhân không tồn tại)"""
    ma_benh_nhan = "ID_KHONG_TON_TAI"
    base_url = "https://localhost:7053/api/v1/patients"
    
    response = requests.get(f"{base_url}/{ma_benh_nhan}/record", headers=HEADERS, verify=False)
    
    assert response.status_code == 404, "Phải báo lỗi 404 Not Found"

@pytest.mark.api
@pytest.mark.error_path
@pytest.mark.security
def test_api3_04_timeline_no_auth():
    """TC_API3_04: Gọi API nhưng không đính kèm Token (Block truy cập)"""
    ma_benh_nhan = "BN_01"
    base_url = "https://localhost:7053/api/v1/patients"
    
    # Cố tình KHÔNG truyền headers để test chặn 401
    response = requests.get(f"{base_url}/{ma_benh_nhan}/record", verify=False)
    
    assert response.status_code == 401, f"Hệ thống phải chặn và báo 401, nhưng lại trả về {response.status_code}"

@pytest.mark.api
@pytest.mark.boundary
@pytest.mark.security
def test_api3_05_timeline_sqli():
    """TC_API3_05: Kiểm thử bảo mật chặn SQL Injection trên URL"""
    ma_benh_nhan = "BN_01' OR '1'='1"
    base_url = "https://localhost:7053/api/v1/patients"
    
    response = requests.get(f"{base_url}/{ma_benh_nhan}/record", headers=HEADERS, verify=False)
    
    # Entity Framework Core bảo vệ chống SQLi, sẽ trả về 404 do không tìm thấy chuỗi ID chứa dấu nháy đơn đó
    assert response.status_code in [400, 404], f"Hệ thống không an toàn nếu trả về {response.status_code}"