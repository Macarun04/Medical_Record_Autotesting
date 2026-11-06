import pytest
import allure
import re
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage

@allure.epic("UI E2E Testing - Medical Record System")
@allure.feature("Xác thực & Đăng nhập (Login UI)")
class TestLoginUI:

    @allure.story("Đăng nhập")
    @allure.title("TC_UI_01: Đăng nhập Bác sĩ thành công chuyển hướng sang search.html")
    @pytest.mark.e2e
    @pytest.mark.smoke
    @pytest.mark.happy_path
    def test_tc_ui_01_login_doctor_success(self, page: Page):
        login_page = LoginPage(page)
        
        with allure.step("Bước 1: Mở trang Đăng nhập"):
            login_page.open()
            page.once("dialog", lambda dialog: dialog.accept())
            
        with allure.step("Bước 2: Nhập tài khoản và mật khẩu Bác sĩ hợp lệ"):
            login_page.login("BS_NguyenVanA", "Password123!")
            
        with allure.step("Bước 3: Xác nhận trình duyệt đã chuyển hướng sang trang tìm kiếm (search.html)"):
            expect(page).to_have_url(re.compile(r".*search\.html"))
            allure.attach(page.screenshot(), name="Login_BacSi_ThanhCong", attachment_type=allure.attachment_type.PNG)

    @allure.story("Đăng nhập")
    @allure.title("TC_UI_02: Bệnh nhân đăng nhập thành công chuyển hướng thẳng vào Timeline")
    @pytest.mark.e2e
    @pytest.mark.happy_path
    def test_tc_ui_02_login_patient_success(self, page: Page):
        login_page = LoginPage(page)
        
        with allure.step("Bước 1: Mở trang Đăng nhập"):
            login_page.open()
            page.once("dialog", lambda dialog: dialog.accept())
            
        with allure.step("Bước 2: Nhập tài khoản và mật khẩu Bệnh nhân hợp lệ"):
            login_page.login("BN_TranThiB", "PatientPass456!") 
            
        with allure.step("Bước 3: Xác nhận Bệnh nhân bị điều hướng thẳng về trang timeline.html kèm mã BN"):
            expect(page).to_have_url(re.compile(r".*timeline\.html\?maBenhNhan=BN_01"))
            allure.attach(page.screenshot(), name="Login_BenhNhan_ThanhCong", attachment_type=allure.attachment_type.PNG)

    @allure.story("Bắt lỗi Form Đăng nhập")
    @allure.title("TC_UI_03: Nhập sai mật khẩu hiển thị thông báo lỗi màu đỏ")
    @pytest.mark.e2e
    @pytest.mark.error_path
    def test_tc_ui_03_login_wrong_password(self, page: Page):
        login_page = LoginPage(page)
        
        with allure.step("Bước 1: Mở trang Đăng nhập và cố tình nhập sai mật khẩu"):
            login_page.open()
            login_page.login("BS_NguyenVanA", "sai_mat_khau_ne")
            
        with allure.step("Bước 2: Kiểm tra thông báo lỗi 'Sai tài khoản hoặc mật khẩu' hiển thị"):
            expect(login_page.error_message).to_be_visible()
            expect(login_page.error_message).to_contain_text("Sai tài khoản hoặc mật khẩu")
            allure.attach(page.screenshot(), name="Thong_Bao_Loi_Sai_Mat_Khau", attachment_type=allure.attachment_type.PNG)

    @allure.story("Bắt lỗi Form Đăng nhập")
    @allure.title("TC_UI_04: Không nhập gì mà bấm Đăng nhập chặn form rỗng (HTML5 Validation)")
    @pytest.mark.e2e
    @pytest.mark.boundary
    def test_tc_ui_04_login_empty_fields(self, page: Page):
        login_page = LoginPage(page)
        
        with allure.step("Bước 1: Mở trang Đăng nhập và để trống các trường, nhấn Submit"):
            login_page.open()
            login_page.login("", "")
            
        with allure.step("Bước 2: Xác nhận trình duyệt chặn thao tác do input bắt buộc (required)"):
            expect(login_page.username_input).to_have_attribute("required", "")
            is_missing = login_page.username_input.evaluate("node => node.validity.valueMissing")
            assert is_missing is True, "Form chưa chặn trạng thái để trống input!"
            allure.attach(page.screenshot(), name="Trinh_Duyet_Chan_Form_Rong", attachment_type=allure.attachment_type.PNG)