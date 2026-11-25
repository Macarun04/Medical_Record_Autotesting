import os
from playwright.sync_api import Page
# Import class BasePage từ file base_page.py
from pages.base_page import BasePage

WEB_BASE_URL = os.getenv("WEB_BASE_URL", "http://localhost:5500")


# Khai báo LoginPage kế thừa BasePage
class LoginPage(BasePage):
    def __init__(self, page: Page):
        # Khởi tạo lớp cha trước để nhận các locator và hàm dùng chung
        super().__init__(page)

        # Chỉ khai báo các định vị đặc thù của trang Login
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_btn = page.locator("button[type='submit']")

        # Trang login dùng ID riêng cho thông báo lỗi, nên ta ghi đè (override) locator của BasePage
        self.error_message = page.locator("#errorMessage")

    def open(self):
        # Sử dụng hàm navigate() đã được định nghĩa ở BasePage để mở trang theo môi trường
        self.navigate(f"{WEB_BASE_URL}/login.html")

    def login(self, username, password):
        """Hành động đăng nhập chuyên biệt của trang này"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()