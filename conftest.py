import os
import random
import allure
import pytest
import requests
import urllib3
from faker import Faker
from playwright.sync_api import Browser, Page

# Tắt cảnh báo InsecureRequestWarning khi gọi HTTPS local không có chứng chỉ
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7053/api/v1")
WEB_BASE_URL = os.getenv("WEB_BASE_URL", "http://localhost:5500")

# Khởi tạo Faker với ngôn ngữ tiếng Việt
fake = Faker("vi_VN")


# ==========================================
# 1. FIXTURES AUTH API (Lấy Token tự động)
# ==========================================
@pytest.fixture(scope="session")
def doctor_headers():
    """Tự động gọi API Đăng nhập bằng tài khoản Bác sĩ, lấy Token."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"tenDangNhap": "BS_NguyenVanA", "matKhau": "Password123!"},
        verify=False,
    )
    if response.status_code == 200:
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    return {"Authorization": "Bearer fake_doctor_token_123"}


@pytest.fixture(scope="session")
def patient_headers():
    """Tự động gọi API Đăng nhập bằng tài khoản Bệnh nhân."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"tenDangNhap": "BN_TranThiB", "matKhau": "PatientPass456!"},
        verify=False,
    )
    if response.status_code == 200:
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}"}
    return {"Authorization": "Bearer fake_patient_token_456"}


# ==========================================
# 2. FIXTURES FAKER (Sinh dữ liệu ngẫu nhiên)
# ==========================================
@pytest.fixture
def fake_patient_data():
    """Tạo payload hồ sơ bệnh nhân ngẫu nhiên, tổ hợp động không trùng lặp."""
    ho = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đỗ", "Bùi", "Hồ", "Ngô", "Dương", "Lý"]
    dem = ["Văn", "Thị", "Đình", "Hữu", "Minh", "Thu", "Thanh", "Hoàng", "Gia", "Bảo"]
    ten = ["An", "Bình", "Cường", "Dung", "Đức", "Hoa", "Hùng", "Linh", "Quân", "Trang", "Hải", "Thảo", "Nam", "Nghĩa", "Phúc"]

    duong = ["Nguyễn Trãi", "Cầu Giấy", "Láng Hạ", "Giải Phóng", "Trần Duy Hưng", "Xã Đàn", "Phố Huế", "Đại Cồ Việt"]
    phuong = ["Phường Mễ Trì", "Phường Thượng Đình", "Phường Dịch Vọng", "Phường Hàng Bột", "Phường Khương Mai"]
    quan = ["Quận Nam Từ Liêm", "Quận Thanh Xuân", "Quận Cầu Giấy", "Quận Đống Đa", "Quận Ba Đình"]

    full_name = f"{random.choice(ho)} {random.choice(dem)} {random.choice(ten)}"
    full_address = (
        f"Số {random.randint(1, 300)} đường {random.choice(duong)}, "
        f"{random.choice(phuong)}, {random.choice(quan)}, Hà Nội"
    )

    return {
        "soCCCD": fake.unique.numerify(text="012#########"),
        "hoVaTen": full_name,
        "ngaySinh": fake.date_of_birth(minimum_age=1, maximum_age=90).strftime("%Y-%m-%dT00:00:00"),
        "gioiTinh": fake.random_element(elements=("Nam", "Nữ")),
        "sdt": fake.numerify(text="09########"),
        "diaChi": full_address,
        "doiTuongBHYT": fake.bothify(text="DN###########"),
    }


@pytest.fixture
def fake_record_data():
    """Tạo payload ca khám ngẫu nhiên."""
    return {
        "trieuChung": fake.sentence(nb_words=10),
        "chanDoan": fake.sentence(nb_words=6),
        "ghiChuDonThuoc": fake.paragraph(nb_sentences=2),
    }


@pytest.fixture
def fake_doctor_data():
    """Tạo payload hồ sơ bác sĩ ngẫu nhiên."""
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
        "Chấn thương chỉnh hình",
    ]

    full_name = f"{random.choice(ho)} {random.choice(dem)} {random.choice(ten)}"

    return {
        "maBacSi": f"BS_{random.randint(1000, 9999)}",
        "tenBacSi": full_name,
        "chuyenKhoa": random.choice(chuyen_khoa),
    }


# ==========================================
# 3. FIXTURES PLAYWRIGHT STORAGE STATE
# ==========================================
@pytest.fixture(scope="session")
def doctor_state_path(browser: Browser):
    """Đăng nhập Bác sĩ 1 lần đầu phiên test và lưu storage_state ra file JSON."""
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    page.goto(f"{WEB_BASE_URL}/login.html", wait_until="networkidle")
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#username").fill("BS_NguyenVanA")
    page.locator("#password").fill("Password123!")
    page.locator("button[type='submit']").click()

    page.wait_for_url("**/search.html")

    state_path = "doctor_state.json"
    context.storage_state(path=state_path)

    context.close()
    yield state_path

    if os.path.exists(state_path):
        os.remove(state_path)


@pytest.fixture
def doctor_page(browser: Browser, doctor_state_path: str):
    """Cung cấp Page đã đăng nhập sẵn quyền Bác sĩ cho từng test case."""
    context = browser.new_context(storage_state=doctor_state_path, ignore_https_errors=True)
    page = context.new_page()
    page.goto(f"{WEB_BASE_URL}/search.html", wait_until="networkidle")

    yield page
    context.close()


# ==========================================
# 4. HOOK ALLURE (Tự động chụp ảnh UI khi Fail)
# ==========================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Tự động chụp màn hình và đính kèm Allure khi test case UI bị FAILED."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = (
            item.funcargs.get("page")
            or item.funcargs.get("doctor_page")
            or item.funcargs.get("patient_page")
        )

        if page:
            screenshot_bytes = page.screenshot(full_page=True)
            os.makedirs("artifacts/screenshots", exist_ok=True)
            with open(f"artifacts/screenshots/{item.name}.png", "wb") as f:
                f.write(screenshot_bytes)
            allure.attach(
                screenshot_bytes,
                name=f"Screenshot_Loi_UI_{item.name}",
                attachment_type=allure.attachment_type.PNG,
            )
            allure.attach(
                page.url,
                name="URL_Tai_Thoi_Diem_Loi",
                attachment_type=allure.attachment_type.TEXT,
            )


@pytest.fixture(autouse=True)
def _force_http_localhost_api(monkeypatch):
    """Đảm bảo mọi lời gọi requests tới https://localhost:7053 đều chuyển sang http://localhost:7053."""
    original_request = requests.Session.request

    def patched_request(self, method, url, *args, **kwargs):
        if isinstance(url, str) and url.startswith("https://localhost:7053"):
            url = url.replace("https://localhost:7053", "http://localhost:7053", 1)
        kwargs.setdefault("verify", False)
        return original_request(self, method, url, *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", patched_request)            