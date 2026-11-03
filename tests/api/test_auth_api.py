import pytest
import requests

# Khai báo URL gốc của Backend (SUT sẽ chạy ở localhost port 5000 hoặc tùy bạn cấu hình ở C#)
BASE_URL = "https://localhost:7053/api/v1/auth/login"

@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.happy_path
def test_api1_01_login_doctor_success():
    """Kiểm tra đăng nhập luồng Bác sĩ hợp lệ"""
    payload = {
        "tenDangNhap": "BS_NguyenVanA",
        "matKhau": "Password123!"
    }
    response = requests.post(BASE_URL, json=payload,verify=False)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "token" in data, "Response thiếu JWT Token"
    assert data["vaiTro"] == "Bác sĩ", "Sai phân quyền vai trò"
    assert "maBacSi" in data, "Response thiếu mã định danh Bác sĩ"

@pytest.mark.api
@pytest.mark.happy_path
def test_api1_02_login_patient_success():
    """Kiểm tra đăng nhập luồng Bệnh nhân hợp lệ"""
    payload = {
        "tenDangNhap": "BN_TranThiB",
        "matKhau": "PatientPass456!"
    }
    response = requests.post(BASE_URL, json=payload, verify=False)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "token" in data
    assert data["vaiTro"] == "Bệnh nhân"
    assert "maBenhNhan" in data

@pytest.mark.api
@pytest.mark.error_path
def test_api1_03_login_wrong_password():
    """Kiểm tra đăng nhập đúng username nhưng sai password"""
    payload = {
        "tenDangNhap": "BS_NguyenVanA",
        "matKhau": "SaiMatKhau!!!"
    }
    response = requests.post(BASE_URL, json=payload, verify=False)
    
    assert response.status_code == 401
    assert "Sai tài khoản hoặc mật khẩu" in response.text

@pytest.mark.api
@pytest.mark.boundary
def test_api1_04_login_empty_data():
    """Kiểm tra gửi request bỏ trống dữ liệu"""
    payload = {
        "tenDangNhap": "",
        "matKhau": ""
    }
    response = requests.post(BASE_URL, json=payload, verify=False)
    
    assert response.status_code == 400

@pytest.mark.api
@pytest.mark.error_path
def test_api1_05_login_invalid_format():
    """Kiểm tra gửi body dạng plain text thay vì JSON"""
    # Gửi data dưới dạng chuỗi text thuần, không dùng tham số json=
    payload_text = "tenDangNhap=BS_NguyenVanA&matKhau=123"
    headers = {'Content-Type': 'text/plain'}
    
    response = requests.post(BASE_URL, data=payload_text, headers=headers, verify=False)
    
    assert response.status_code in [400,415]

