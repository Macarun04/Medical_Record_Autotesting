import pytest
import requests
import random

BASE_URL = "https://localhost:7053/api/v1/patients"

def generate_random_cccd():
    """Hàm hỗ trợ sinh ngẫu nhiên 12 số CCCD để test không bị trùng khi chạy nhiều lần"""
    return f"012{random.randint(100000000, 999999999)}"

@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.happy_path
def test_api5_01_create_patient_success():
    """TC_API5_01: Tạo hồ sơ bệnh nhân mới đầy đủ thông tin"""
    payload = {
        "soCCCD": generate_random_cccd(),
        "hoVaTen": "Trần Thị B",
        "ngaySinh": "1990-05-20T00:00:00",
        "gioiTinh": "Nữ",
        "sdt": "0901234567",
        "diaChi": "Quận 1, TP.HCM",
        "doiTuongBHYT": "DN123456789"
    }
    response = requests.post(BASE_URL, json=payload, verify=False)

    print("\n>>> LỖI C# BÁO VỀ LÀ:", response.text)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert "maBenhNhan" in data or "maBenhNhan" in data.get("data", {}), "Phải tự động sinh maBenhNhan"

@pytest.mark.api
@pytest.mark.error_path
def test_api5_02_create_patient_duplicate():
    """TC_API5_02: Trùng lặp số CCCD đã tồn tại trong DB"""
    cccd_trung = generate_random_cccd()
    payload = {
        "soCCCD": cccd_trung,
        "hoVaTen": "Nguyễn Văn Chống Trùng",
        "ngaySinh": "1995-10-10T00:00:00",
        "gioiTinh": "Nam"
    }
    # Gọi lần 1: Đẩy dữ liệu vào DB (201 Created)
    requests.post(BASE_URL, json=payload, verify=False)
    
    # Gọi lần 2: Gửi y hệt data cũ, mong đợi bị C# chặn lại
    response = requests.post(BASE_URL, json=payload, verify=False)
    
    assert response.status_code == 409, f"Expected 409 Conflict, got {response.status_code}"

@pytest.mark.api
@pytest.mark.boundary
def test_api5_03_create_patient_missing_req():
    """TC_API5_03: Bỏ trống trường bắt buộc (Xóa hoVaTen và ngaySinh)"""
    payload = {
        "soCCCD": generate_random_cccd(),
        "gioiTinh": "Nữ",
        "sdt": "0901234567",
        "diaChi": "Quận 1, TP.HCM"
        # Cố tình không truyền hoVaTen và ngaySinh
    }
    response = requests.post(BASE_URL, json=payload, verify=False)
    
    assert response.status_code == 400, "Phải bắt được lỗi 400 Bad Request do thiếu trường"

@pytest.mark.api
@pytest.mark.boundary
def test_api5_04_create_patient_min_data():
    """TC_API5_04: Nhập tối giản dữ liệu (Chỉ truyền trường bắt buộc, bỏ sdt và diaChi)"""
    payload = {
        "soCCCD": generate_random_cccd(),
        "hoVaTen": "Lê Văn Tối Giản",
        "ngaySinh": "2000-01-01T00:00:00",
        "gioiTinh": "Nam"
        # Bỏ trống sdt, diaChi, doiTuongBHYT
    }
    response = requests.post(BASE_URL, json=payload, verify=False)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

@pytest.mark.api
@pytest.mark.error_path
def test_api5_05_create_patient_bad_date():
    """TC_API5_05: Sai định dạng DateTime (Nhập ngày 32/13)"""
    payload = {
        "soCCCD": generate_random_cccd(),
        "hoVaTen": "Hoàng Thị Sai Ngày",
        "ngaySinh": "32/13/1990", # Cố tình truyền string ngày sai logic
        "gioiTinh": "Nữ"
    }
    response = requests.post(BASE_URL, json=payload, verify=False)
    
    assert response.status_code == 400, "ASP.NET Core phải tự động chặn ngày tháng không hợp lệ (400)"