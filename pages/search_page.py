from playwright.sync_api import Page
from pages.base_page import BasePage

class SearchPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Locators
        self.cccd_input = page.get_by_test_id("input-search-cccd")
        self.search_button = page.get_by_test_id("btn-search")
        self.patient_info_card = page.get_by_test_id("card-patient-info")
        self.btn_view_timeline = page.get_by_test_id("btn-view-timeline")

    def search_by_cccd(self, cccd: str):
        """Hành vi tra cứu CCCD"""
        self.cccd_input.fill(cccd)
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")

    def is_patient_found(self) -> bool:
        """Kiểm tra thẻ thông tin bệnh nhân có xuất hiện không"""
        return self.patient_info_card.is_visible()

    def go_to_timeline(self):
        """Bấm nút chuyển sang màn hình Timeline sau khi tìm thấy"""
        self.btn_view_timeline.click()
        self.page.wait_for_load_state("networkidle")

from playwright.sync_api import Page

class SearchPage:
    def __init__(self, page: Page):
        self.page = page
        self.search_input = page.locator("#searchInput")
        self.patient_card = page.locator("#patientCard")
        self.empty_state = page.locator("#emptyState")
        self.error_message = page.locator("#errorMessage")
        
        # Các trường thông tin trên thẻ
        self.val_hoten = page.locator("#valHoTen")
        self.val_cccd = page.locator("#valCCCD")

    def search_cccd(self, cccd):
        self.search_input.fill(cccd)
        self.search_input.press("Enter")