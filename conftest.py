import pytest
import requests
import urllib3
import allure
from faker import Faker

# Tắt cảnh báo InsecureRequestWarning khi gọi https://localhost mà không có chứng chỉ
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:7053/api/v1"

# Khởi tạo Faker với ngôn ngữ tiếng Việt
fake = Faker('vi_VN')

# ==========================================
# 1. FIXTURES AUTH (Lấy Token tự động)
# ==========================================
@pytest.fixture(scope="session")
def doctor_headers():
    """Tự động gọi API Đăng nhập bằng tài khoản Bác sĩ, lấy Token."""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "tenDangNhap": "BS_NguyenVanA",
        "matKhau": "Password123!"
    }, verify=False)
    
    if response.status_code == 200:
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    return {"Authorization": "Bearer fake_doctor_token_123"}

@pytest.fixture(scope="session")
def patient_headers():
    """Tự động gọi API Đăng nhập bằng tài khoản Bệnh nhân."""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "tenDangNhap": "BN_TranThiB",
        "matKhau": "PatientPass456!"
    }, verify=False)
    
    if response.status_code == 200:
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    return {"Authorization": "Bearer fake_patient_token_456"}


# ==========================================
# 2. FIXTURES FAKER (Sinh dữ liệu ngẫu nhiên)
# ==========================================
import random

@pytest.fixture
def fake_patient_data():
    """Tạo payload hồ sơ bệnh nhân ngẫu nhiên, tổ hợp động hàng nghìn kiểu không lặp"""
    
    ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đỗ", "Bùi", "Hồ", "Ngô", "Dương", "Lý"]
    dem = ["Văn", "Thị", "Đình", "Hữu", "Minh", "Thu", "Thanh", "Hoàng", "Gia", "Bảo"]
    ten = ["An", "Bình", "Cường", "Dung", "Đức", "Hoa", "Hùng", "Linh", "Quân", "Trang", "Hải", "Thảo", "Nam", "Nghĩa", "Phúc"]
    
    duong = ["Nguyễn Trãi", "Cầu Giấy", "Láng Hạ", "Giải Phóng", "Trần Duy Hưng", "Xã Đàn", "Phố Huế", "Đại Cồ Việt"]
    phuong = ["Phường Mễ Trì", "Phường Thượng Đình", "Phường Dịch Vọng", "Phường Hàng Bột", "Phường Khương Mai"]
    quan = ["Quận Nam Từ Liêm", "Quận Thanh Xuân", "Quận Cầu Giấy", "Quận Đống Đa", "Quận Ba Đình"]

    # Ghép tổ hợp tên: Hàng chục x Hàng chục x Hàng chục = Hàng nghìn tên khác nhau
    full_name = f"{random.choice(ho)} {random.choice(dem)} {random.choice(ten)}"
    
    # Ghép tổ hợp địa chỉ
    full_address = f"Số {random.randint(1, 300)} đường {random.choice(duong)}, {random.choice(phuong)}, {random.choice(quan)}, Hà Nội"

    return {
        "soCCCD": fake.unique.numerify(text="012#########"), # 12 số không trùng nhau
        "hoVaTen": full_name,
        "ngaySinh": fake.date_of_birth(minimum_age=1, maximum_age=90).strftime("%Y-%m-%dT00:00:00"),
        "gioiTinh": fake.random_element(elements=("Nam", "Nữ")),
        "sdt": fake.numerify(text="09########"), 
        "diaChi": full_address,
        "doiTuongBHYT": fake.bothify(text="DN###########")
    }

@pytest.fixture
def fake_record_data():
    """Tạo payload ca khám ngẫu nhiên (chưa gồm mã BN và mã BS, sẽ ghép vào trong test)"""
    return {
        "trieuChung": fake.sentence(nb_words=10),
        "chanDoan": fake.sentence(nb_words=6),
        "ghiChuDonThuoc": fake.paragraph(nb_sentences=2)
    }


# ==========================================
# 3. HOOK ALLURE (Tự động chụp ảnh UI khi Fail)
# ==========================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook này can thiệp vào quá trình chạy test.
    Nếu một test case UI (sử dụng Playwright page) bị đánh giá là FAILED,
    hệ thống sẽ tự động chụp màn hình và đính kèm vào báo cáo Allure.
    """
    outcome = yield
    report = outcome.get_result()

    # Chỉ xử lý khi test case thực sự fail ở bước thực thi (call)
    if report.when == "call" and report.failed:
        # Lấy đối tượng 'page' từ Playwright (nếu test case đó có truyền tham số page)
        page = item.funcargs.get("page", None)
        
        if page:
            # Chụp toàn bộ màn hình trình duyệt tại thời điểm lỗi
            screenshot_bytes = page.screenshot(full_page=True)
            
            # Đính kèm ảnh vào báo cáo Allure
            allure.attach(
                screenshot_bytes,
                name=f"Screenshot_Loi_UI_{item.name}",
                attachment_type=allure.attachment_type.PNG
            )
            
            # Đính kèm log URL hiện tại để tiện debug
            allure.attach(
                page.url,
                name="URL_Tai_Thoi_Diem_Loi",
                attachment_type=allure.attachment_type.TEXT
            )

# FAKER SINH DỮ LIỆU BÁC SĨ NGẪU NHIÊN
@pytest.fixture
def fake_doctor_data():
    """Tạo payload hồ sơ bác sĩ ngẫu nhiên, tổ hợp động từ các mảng từ vựng tiếng Việt chuyên nghiệp"""
    
    ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đỗ", "Bùi", "Hồ", "Ngô"]
    dem = ["Văn", "Thị", "Đình", "Hữu", "Minh", "Thu", "Thanh", "Hoàng", "Gia", "Hồng"]
    ten = ["An", "Bình", "Cường", "Dung", "Đức", "Hoa", "Hùng", "Linh", "Quân", "Trang", "Hải", "Thảo", "Nam", "Sơn", "Tùng"]
    
    chuyen_khoa = [
        "Nội khoa", 
        "Ngoại khoa", 
        "Nhi khoa", 
        "Sản phụ khoa", 
        "Da liễu", 
        "Tai Mũi Họng", 
        "Mắt", 
        "Tim mạch",
        "Thần kinh",
        "Chấn thương chỉnh hình"
    ]

    # Ghép tổ hợp tên bác sĩ: Họ + Đệm + Tên
    full_name = f"{random.choice(ho)} {random.choice(dem)} {random.choice(ten)}"

    return {
        "maBacSi": f"BS_{random.randint(1000, 9999)}", # Mã bác sĩ ngẫu nhiên tránh trùng lặp
        "tenBacSi": full_name,
        "chuyenKhoa": random.choice(chuyen_khoa)
    }