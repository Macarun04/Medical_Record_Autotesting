import pytest
import requests

BASE_URL = "https://localhost:7053/api/v1/patients/search"

@pytest.mark.api
@pytest.mark.happy_path
def test_api2_01_search_valid_cccd(doctor_headers):
    """TC_API2_01: Tra cứu CCCD hợp lệ có trong DB"""
    response = requests.get(f"{BASE_URL}?cccd=012345678912", headers=doctor_headers, verify=False)
    
    assert response.status_code == 200
    data = response.json()
    assert data["soCCCD"] == "012345678912"
    assert "maBenhNhan" in data

@pytest.mark.api
@pytest.mark.error_path
def test_api2_02_search_not_found(doctor_headers):
    """TC_API2_02: CCCD đúng định dạng 12 số nhưng không tồn tại"""
    response = requests.get(f"{BASE_URL}?cccd=999999999999", headers=doctor_headers, verify=False)
    
    assert response.status_code == 404
    # Nếu API của bạn không trả về text chứa "Không tìm thấy", bạn có thể bỏ dòng assert dưới
    assert "Không tìm thấy" in response.text 

@pytest.mark.api
@pytest.mark.boundary
def test_api2_03_search_invalid_length(doctor_headers):
    """TC_API2_03: CCCD sai độ dài (9 số hoặc 13 số thay vì 12 số)"""
    response = requests.get(f"{BASE_URL}?cccd=123456789", headers=doctor_headers, verify=False)
    
    assert response.status_code == 400

@pytest.mark.api
@pytest.mark.boundary
def test_api2_04_search_special_chars(doctor_headers):
    """TC_API2_04: CCCD chứa ký tự lạ/chữ cái"""
    response = requests.get(f"{BASE_URL}?cccd=01234567891a", headers=doctor_headers, verify=False)
    
    assert response.status_code == 400

@pytest.mark.api
@pytest.mark.boundary
def test_api2_05_search_missing_param(doctor_headers):
    """TC_API2_05: Không truyền tham số cccd trên URL"""
    response = requests.get(BASE_URL, headers=doctor_headers, verify=False)
    
    assert response.status_code == 400
