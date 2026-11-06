# pages/search_page.py
from playwright.sync_api import Page
from pages.base_page import BasePage

class SearchPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Thống nhất Locators dựa theo file search.html
        # Thêm dòng này vào hàm __init__
        self.val_ma_bn = page.locator("#valMaBN")
        self.search_input = page.locator("#searchInput")
        self.search_button = page.locator("#btn-search") # (hoặc bỏ qua nếu file HTML của bạn chỉ cần bấm Enter)
        
        self.patient_card = page.locator("#patientCard")
        self.empty_state = page.locator("#emptyState")
        self.error_message = page.locator("#errorMessage")
        
        # Các trường thông tin trên thẻ
        self.val_hoten = page.locator("#valHoTen")
        self.val_cccd = page.locator("#valCCCD")
        
        self.btn_view_timeline = page.locator("#btnGoTimeline") # Cập nhật theo HTML thực tế

    def search_cccd(self, cccd: str):
        """Hành vi tra cứu CCCD bằng cách nhập và ấn Enter"""
        self.search_input.fill(cccd)
        self.search_input.press("Enter")
        # Đợi hệ thống gọi API và tải dữ liệu xong
        self.page.wait_for_load_state("networkidle")

    def is_patient_found(self) -> bool:
        """Kiểm tra thẻ thông tin bệnh nhân có xuất hiện không"""
        return self.patient_card.is_visible()

    def go_to_timeline(self):
        """Bấm nút Xem Timeline"""
        self.btn_view_timeline.click()
        self.page.wait_for_load_state("networkidle")