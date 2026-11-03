from playwright.sync_api import Page





class BasePage:
    def __init__(self, page: Page):
        self.page = page
        # Locator chung cho các thông báo (Toast message / Error message)
        self.toast_message = page.get_by_test_id("toast-message")
        self.error_message = page.get_by_test_id("error-message")

    def navigate(self, url: str):
        """Điều hướng đến một URL cụ thể"""
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    def get_toast_text(self) -> str:
        """Lấy nội dung thông báo thành công (Toast)"""
        self.toast_message.wait_for(state="visible")
        return self.toast_message.inner_text()

    def get_error_text(self) -> str:
        """Lấy nội dung thông báo lỗi chung"""
        self.error_message.wait_for(state="visible")
        return self.error_message.inner_text()

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        # Định vị các phần tử dựa trên ID trong mã HTML của bạn
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_btn = page.locator("button[type='submit']")
        self.error_message = page.locator("#errorMessage")

    def open(self):
        # Bạn cần chạy thư mục SUT_FrontEnd qua Live Server (vd: http://127.0.0.1:5500)
        self.page.goto("http://127.0.0.1:5500/.pytest_cache/SUT_FrontEnd/login.html")

    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()