import pytest
import allure
import re
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.timeline_page import TimelinePage

@allure.epic("UI E2E Testing - Medical Record System")
@allure.feature("Giao diện Bệnh nhân (Patient UI)")
class TestPatientUI:

    @allure.story("Xem Lịch sử khám cá nhân")
    @allure.title("TC_UI_10: Bệnh nhân xem đúng timeline của mình, không thấy nút 'Tạo ca khám'")
    @pytest.mark.e2e
    @pytest.mark.happy_path
    @pytest.mark.security
    def test_tc_ui_10_patient_view_own_timeline(self, page: Page):
        login_page = LoginPage(page)
        timeline_page = TimelinePage(page)
        
        with allure.step("Bước 1: Bệnh nhân đăng nhập thành công vào hệ thống"):
            login_page.open()
            page.once("dialog", lambda dialog: dialog.accept())
            login_page.login("BN_TranThiB", "PatientPass456!") 
            
        with allure.step("Bước 2: Kiểm tra trình duyệt điều hướng chính xác vào timeline cá nhân"):
            expect(page).to_have_url(re.compile(r".*timeline\.html\?maBenhNhan=BN_01"))
            expect(timeline_page.banner_ma_bn).to_have_text("BN_01")
            expect(timeline_page.timeline_container).to_be_visible()
            
        with allure.step("Bước 3: Đảm bảo nút 'Thêm ca khám mới' BỊ ẨN ĐI đối với Bệnh nhân (Phân quyền UI)"):
            expect(timeline_page.btn_add_new_record).to_be_hidden()
            allure.attach(page.screenshot(), name="Giao_Dien_Timeline_Phan_Quyen_Benh_Nhan", attachment_type=allure.attachment_type.PNG)