from playwright.sync_api import Page
from pages.base_page import BasePage

class TimelinePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        
        # 1. Các locator cho Banner thông tin bệnh nhân
        self.banner_ma_bn = page.locator("#bannerMaBN")
        
        # 2. Các nút bấm hành động
        self.btn_add_new_record = page.locator("#btnAddRecord")
        self.btn_save_record = page.locator("button.btn-save")
        
        # 3. Vùng chứa danh sách và modal
        self.timeline_container = page.locator("#timelineContainer")
        self.record_modal = page.locator("#recordModal")
        self.record_cards = page.locator(".record-card")
        
        # 4. Các trường input trong modal thêm ca khám
        self.input_trieu_chung = page.locator("textarea#inputTrieuChung")
        self.input_chan_doan = page.locator("textarea#inputChanDoan")
        self.input_ghi_chu = page.locator("textarea#inputGhiChu")