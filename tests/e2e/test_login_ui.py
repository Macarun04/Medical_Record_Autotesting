import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
import re

@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.happy_path
def test_tc_ui_01_login_doctor_success(page: Page):
    """TC_UI_01: Đăng nhập Bác sĩ thành công chuyển hướng sang search.html"""
    login_page = LoginPage(page)
    login_page.open()
    
    # Xử lý Alert "Đăng nhập thành công..." của JavaScript trước khi nó hiện ra
    page.once("dialog", lambda dialog: dialog.accept())
    
    login_page.login("BS_NguyenVanA", "Password123!") # Dùng tài khoản thật trong DB
    
    # Chờ và xác nhận trình duyệt đã chuyển sang trang tìm kiếm
    expect(page).to_have_url(re.compile(r".*search\.html"))


@pytest.mark.e2e
@pytest.mark.happy_path
def test_tc_ui_02_login_patient_success(page: Page):
    """TC_UI_02: Bệnh nhân đăng nhập thành công chuyển hướng thẳng vào Timeline của họ"""
    login_page = LoginPage(page)
    login_page.open()
    
    # Xử lý Alert "Đăng nhập thành công..." của JavaScript trước khi nó hiện ra
    page.once("dialog", lambda dialog: dialog.accept())
    
    # Sử dụng đúng tài khoản Bệnh nhân trong DB của bạn
    login_page.login("BN_TranThiB", "PatientPass456!") 
    
    # Xác nhận hệ thống phân quyền đúng: Bệnh nhân bị đẩy về trang timeline kèm mã định danh trên URL
    expect(page).to_have_url(re.compile(r".*timeline\.html\?maBenhNhan=BN_01"))


@pytest.mark.e2e
@pytest.mark.error_path
def test_tc_ui_03_login_wrong_password(page: Page):
    """TC_UI_03: Nhập sai mật khẩu hiển thị chữ đỏ"""
    login_page = LoginPage(page)
    login_page.open()
    
    # Cố tình nhập sai mật khẩu
    login_page.login("BS_NguyenVanA", "sai_mat_khau_ne")
    
    # Kiểm tra dòng text báo lỗi phải xuất hiện trên màn hình
    expect(login_page.error_message).to_be_visible()
    expect(login_page.error_message).to_contain_text("Sai tài khoản hoặc mật khẩu")


@pytest.mark.e2e
@pytest.mark.boundary
def test_tc_ui_04_login_empty_fields(page: Page):
    """TC_UI_04: Không nhập gì mà bấm Đăng nhập chặn form rỗng (HTML5 Validation)"""
    login_page = LoginPage(page)
    login_page.open()
    
    # Để trống hoàn toàn và bấm đăng nhập
    login_page.login("", "")
    
    # Playwright kiểm tra ô username phải có thuộc tính required
    expect(login_page.username_input).to_have_attribute("required", "")
    
    # Xác nhận thêm bằng Javascript: Trình duyệt thực sự bật trạng thái báo lỗi bỏ trống (valueMissing)
    is_missing = login_page.username_input.evaluate("node => node.validity.valueMissing")
    assert is_missing is True, "Form chưa chặn trạng thái để trống input!"