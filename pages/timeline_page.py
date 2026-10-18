from playwright.sync_api import Page
from pages.base_page import BasePage

class TimelinePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Locators
        self.patient_header = page.get_by_test_id("timeline-patient-header")
        self.record_cards = page.get_by_test_id("record-card") # Bắt toàn bộ các thẻ ca khám
        self.empty_state = page.get_by_test_id("empty-state-message")
        self.btn_add_new_record = page.get_by_test_id("btn-add-record")

    def get_record_count(self) -> int:
        """Đếm số lượng ca khám hiển thị trên Timeline"""
        return self.record_cards.count()

    def is_empty_state_visible(self) -> bool:
        """Kiểm tra xem dòng chữ 'Chưa có dữ liệu ca khám' có hiển thị không"""
        return self.empty_state.is_visible()

    def get_first_record_diagnose(self) -> str:
        """Lấy chẩn đoán của ca khám mới nhất (nằm trên cùng)"""
        # first() để lấy phần tử đầu tiên trong mảng các card
        first_card = self.record_cards.first
        return first_card.get_by_test_id("text-chandoan").inner_text()
        
    def click_add_new_record(self):
        """Bấm nút chuyển sang màn hình thêm ca khám"""
        self.btn_add_new_record.click()