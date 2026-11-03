import pytest
import requests

BASE_URL = "https://localhost:7053/api/v1/records"

# Token giả lập phục vụ cho các test case phân quyền
HEADERS_DOCTOR = {"Authorization": "Bearer BearerToken_Doctor_Valid"}
HEADERS_PATIENT = {"Authorization": "Bearer BearerToken_Patient_BN01"}

@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.happy_path
def test_api4_01_create_record_success():
    """TC_API4_01: Tạo ca khám đầy đủ thông tin (Token Bác sĩ)"""
    payload = {
        "maBenhNhan": "BN_01",
        "maBacSi": "BS_01",
        "trieuChung": "Ho khan, sốt nhẹ",
        "chanDoan": "Viêm họng cấp",
        "ghiChuDonThuoc": "Kháng sinh 5 ngày, tái khám sau 1 tuần"
    }
    
    response = requests.post(BASE_URL, json=payload, headers=HEADERS_DOCTOR, verify=False)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert "maCaKham" in data.get("data", {}) or "maCaKham" in data, "Phải trả về mã ca khám"

@pytest.mark.api
@pytest.mark.boundary
def test_api4_02_create_record_opt_field():
    """TC_API4_02: Tạo ca khám thiếu trường tùy chọn (ghiChuDonThuoc để trống/null)"""
    payload = {
        "maBenhNhan": "BN_01",
        "maBacSi": "BS_01",
        "trieuChung": "Đau đầu chóng mặt",
        "chanDoan": "Thiếu máu não",
        "ghiChuDonThuoc": None # Bỏ trống tùy chọn theo đúng ma trận
    }
    
    response = requests.post(BASE_URL, json=payload, headers=HEADERS_DOCTOR, verify=False)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

@pytest.mark.api
@pytest.mark.error_path
def test_api4_03_create_record_missing():
    """TC_API4_03: Bỏ trống các trường bắt buộc (thiếu hoặc để trống maBenhNhan)"""
    payload = {
        "maBenhNhan": "", # Cố tình để trống trường bắt buộc
        "maBacSi": "BS_01",
        "trieuChung": "Sốt cao",
        "chanDoan": "Sốt xuất huyết"
    }
    
    response = requests.post(BASE_URL, json=payload, headers=HEADERS_DOCTOR, verify=False)
    
    assert response.status_code == 400, "Phải trả về 400 Bad Request do thiếu trường bắt buộc"

@pytest.mark.api
@pytest.mark.boundary
def test_api4_04_create_record_max_len():
    """TC_API4_04: Vượt giới hạn ký tự DB (Trường trieuChung dài 2001 ký tự)"""
    payload = {
        "maBenhNhan": "BN_01",
        "maBacSi": "BS_01",
        "trieuChung": "A" * 2001, # Cố tình tạo chuỗi dài 2001 ký tự vượt ngưỡng 2000
        "chanDoan": "Kiểm tra giới hạn ký tự"
    }
    
    response = requests.post(BASE_URL, json=payload, headers=HEADERS_DOCTOR, verify=False)
    
    # C# / Entity Framework hoặc Database sẽ từ chối lưu và trả về 400 Bad Request
    assert response.status_code == 400, "Phải báo 400 Bad Request khi vượt quá giới hạn ký tự"

@pytest.mark.api
@pytest.mark.error_path
@pytest.mark.security
def test_api4_05_create_record_wrong_role():
    """TC_API4_05: Phân quyền sai vai trò (Dùng Token của Bệnh nhân để gọi POST)"""
    payload = {
        "maBenhNhan": "BN_01",
        "maBacSi": "BS_01",
        "trieuChung": "Đau bụng",
        "chanDoan": "Đau dạ dày"
    }
    
    # Sử dụng headers của Bệnh nhân thay vì Bác sĩ
    response = requests.post(BASE_URL, json=payload, headers=HEADERS_PATIENT, verify=False)
    
    assert response.status_code == 403, "Phải trả về 403 Forbidden do sai phân quyền"