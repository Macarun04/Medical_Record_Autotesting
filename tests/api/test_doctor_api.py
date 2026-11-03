import pytest
import requests

BASE_URL = "https://localhost:7053/api/v1/doctors"

# Token hợp lệ dùng cho các test case yêu cầu đăng nhập (TC 01 đến 04)
HEADERS_VALID = {"Authorization": "Bearer BearerToken_Doctor_Valid"}

@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.happy_path
def test_api6_01_doctors_get_all():
    """TC_API6_01_Doctors_GetAll: Lấy toàn bộ danh sách bác sĩ không truyền query param"""
    response = requests.get(BASE_URL, headers=HEADERS_VALID, verify=False)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, list), "Response phải là một mảng danh sách"
    if len(data) > 0:
        assert "maBacSi" in data[0], "Mỗi object bác sĩ phải có trường maBacSi"

@pytest.mark.api
@pytest.mark.happy_path
def test_api6_02_doctors_filter_exist():
    """TC_API6_02_Doctors_FilterExist: Lọc theo khoa đang có người (Nội khoa)"""
    response = requests.get(f"{BASE_URL}?chuyenKhoa=Nội khoa", headers=HEADERS_VALID, verify=False)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, list)
    for doctor in data:
        assert doctor["chuyenKhoa"] == "Nội khoa", "Tất cả bác sĩ trả về phải thuộc khoa Nội khoa"

@pytest.mark.api
@pytest.mark.boundary
def test_api6_03_doctors_filter_empty():
    """TC_API6_03_Doctors_FilterEmpty: Lọc theo khoa chưa có người (Nha khoa)"""
    response = requests.get(f"{BASE_URL}?chuyenKhoa=Nha khoa", headers=HEADERS_VALID, verify=False)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0, "Khoa chưa có data phải trả về mảng rỗng []"

@pytest.mark.api
@pytest.mark.boundary
def test_api6_04_doctors_encoding():
    """TC_API6_04_Doctors_Encoding: Truyền ký tự mã hóa URL/UTF-8 (?chuyenKhoa=Nội%20khoa)"""
    response = requests.get(f"{BASE_URL}?chuyenKhoa=Nội%20khoa", headers=HEADERS_VALID, verify=False)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, list)
    # Hệ thống phải tự động decode %20 thành khoảng trắng và trả data đúng
    for doctor in data:
        assert doctor["chuyenKhoa"] == "Nội khoa"

@pytest.mark.api
@pytest.mark.error_path
@pytest.mark.security
def test_api6_05_doctors_no_auth():
    """TC_API6_05_Doctors_NoAuth: Block truy cập không ủy quyền (Không truyền Token)"""
    # Cố tình KHÔNG truyền headers để kiểm tra cơ chế bảo mật trả về 401
    response = requests.get(BASE_URL, verify=False)
    
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"