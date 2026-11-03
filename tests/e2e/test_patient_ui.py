import pytest
import re
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage

@pytest.mark.e2e
@pytest.mark.happy_path
@pytest.mark.security
def test_tc_ui_10_patient_view_own_timeline(page: Page):
    """TC_UI_10: Bệnh nhân xem đúng timeline của mình (Đảm bảo phân quyền bảo mật)"""
    
    # 1. Đăng nhập hệ thống bằng tài khoản Bệnh nhân
    login_page = LoginPage(page)
    login_page.open()
    
    # Xử lý Alert "Đăng nhập thành công"
    page.once("dialog", lambda dialog: dialog.accept())
    
    # Sử dụng đúng tài khoản Bệnh nhân có thật trong DB
    login_page.login("BN_TranThiB", "PatientPass456!") 
    
    # 2. Quan sát giao diện hiển thị
    # KQMĐ 1: Hệ thống tự động đẩy về trang timeline khớp với định danh của chính bệnh nhân đó
    expect(page).to_have_url(re.compile(r".*timeline\.html\?maBenhNhan=BN_01"))
    
    # KQMĐ 2: Banner thông tin phải hiển thị đúng mã BN của mình, không tải nhầm dữ liệu người khác
    expect(page.locator("#bannerMaBN")).to_have_text("BN_01")
    
    # KQMĐ 3 (Security Check): Đảm bảo giao diện chặn quyền, Bệnh nhân KHÔNG thấy nút "Thêm ca khám"
    add_record_btn = page.locator("button#btnAddRecord")
    expect(add_record_btn).to_be_hidden()
    
    # KQMĐ 4: Container chứa lịch sử ca khám phải được hiển thị bình thường
    timeline_container = page.locator("#timelineContainer")
    expect(timeline_container).to_be_visible()