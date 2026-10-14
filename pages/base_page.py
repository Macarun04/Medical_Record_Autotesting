from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        self.page.goto(url)

    # Hàm hỗ trợ lấy locator theo chuẩn data-testid
    def get_by_testid(self, test_id: str):
        return self.page.get_by_test_id(test_id)