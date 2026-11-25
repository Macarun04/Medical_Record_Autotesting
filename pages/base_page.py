# pages/base_page.py
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.toast_message = page.get_by_test_id("toast-message")
        self.error_message = page.get_by_test_id("error-message")

    def navigate(self, url: str):
        """Điều hướng đến một URL cụ thể."""
        self.page.goto(url, wait_until="domcontentloaded")

    def get_toast_text(self) -> str:
        """Lấy nội dung thông báo thành công (Toast)."""
        self.toast_message.wait_for(state="visible")
        return self.toast_message.inner_text()

    def get_error_text(self) -> str:
        """Lấy nội dung thông báo lỗi chung."""
        self.error_message.wait_for(state="visible")
        return self.error_message.inner_text()