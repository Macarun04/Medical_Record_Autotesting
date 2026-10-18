from playwright.sync_api import Page
from pages.base_page import BasePage

class AddRecordPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Locators
        self.chuyen_khoa_input = page.get_by_test_id("input-chuyenkhoa")
        self.trieu_chung_input = page.get_by_test_id("input-trieuchung")
        self.chan_doan_input = page.get_by_test_id("input-chandoan")
        self.don_thuoc_input = page.get_by_test_id("input-donthuoc")
        self.save_button = page.get_by_test_id("btn-save-record")

    def fill_record_form(self, chuyen_khoa: str, trieu_chung: str, chan_doan: str, don_thuoc: str = ""):
        """Điền thông tin vào form ca khám"""
        self.chuyen_khoa_input.fill(chuyen_khoa)
        self.trieu_chung_input.fill(trieu_chung)
        self.chan_doan_input.fill(chan_doan)
        
        if don_thuoc:
            self.don_thuoc_input.fill(don_thuoc)

    def submit_form(self):
        """Bấm nút Lưu ca khám"""
        self.save_button.click()
        # Đợi hệ thống gọi API POST /api/v1/records
        self.page.wait_for_load_state("networkidle")