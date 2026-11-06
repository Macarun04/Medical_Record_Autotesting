import pytest
import re
import allure
from faker import Faker
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from pages.timeline_page import TimelinePage

fake = Faker('vi_VN')

# Có thể bọc hàm helper này vào một step chung để log luôn trên Allure
@allure.step("Tiền quyết: Đăng nhập sẵn vào tài khoản Bác sĩ")
def login_as_doctor(page: Page):
    login_page = LoginPage(page)
    login_page.open()
    page.once("dialog", lambda dialog: dialog.accept())
    login_page.login("BS_NguyenVanA", "Password123!")
    expect(page).to_have_url(re.compile(r".*search\.html"))


@allure.epic("UI E2E Testing - Medical Record System")
@allure.feature("Giao diện Bác sĩ (Doctor UI)")
class TestDoctorUI:

    @allure.story("Tra cứu Bệnh nhân")
    @allure.title("TC_UI_05: Bác sĩ tra cứu CCCD thành công")
    @pytest.mark.e2e
    @pytest.mark.smoke
    @pytest.mark.happy_path
    def test_tc_ui_05_doctor_search_patient_success(self, page: Page):
        login_as_doctor(page)
        search_page = SearchPage(page)
        
        with allure.step("Bước 1: Bác sĩ nhập số CCCD hợp lệ và bấm tra cứu"):
            search_page.search_cccd("012345678912")
            
        with allure.step("Bước 2: Kiểm tra thẻ thông tin bệnh nhân hiển thị đầy đủ dữ liệu"):
            expect(search_page.patient_card).to_be_visible()
            expect(search_page.val_ma_bn).not_to_have_text("---")
            expect(search_page.val_cccd).not_to_have_text("---")
            expect(search_page.val_hoten).not_to_have_text("---")
            
            # Đính kèm ảnh chụp màn hình kết quả tìm kiếm thành công vào Allure
            allure.attach(page.screenshot(), name="Ket_Qua_Tim_Kiem_Thanh_Cong", attachment_type=allure.attachment_type.PNG)


    @allure.story("Tra cứu Bệnh nhân")
    @allure.title("TC_UI_06: Bác sĩ tra cứu CCCD không có thật (đủ 12 số)")
    @pytest.mark.e2e
    @pytest.mark.error_path
    def test_tc_ui_06_doctor_search_not_found(self, page: Page):
        login_as_doctor(page)
        search_page = SearchPage(page)
        
        with allure.step("Bước 1: Bác sĩ nhập CCCD lạ (999999999999) và bấm tra cứu"):
            search_page.search_cccd("999999999999")
            
        with allure.step("Bước 2: Kiểm tra thông báo lỗi hiển thị chữ đỏ đúng nội dung"):
            expect(search_page.error_message).to_be_visible()
            expect(search_page.error_message).to_have_text("Không tìm thấy hồ sơ bệnh nhân với số CCCD này!")
            allure.attach(page.screenshot(), name="Thong_Bao_Loi_Tim_Kiem", attachment_type=allure.attachment_type.PNG)


    @allure.story("Quản lý Timeline Bệnh án")
    @allure.title("TC_UI_07: Bác sĩ xem lịch sử ca khám của bệnh nhân (timeline)")
    @pytest.mark.e2e
    @pytest.mark.happy_path
    def test_tc_ui_07_doctor_view_timeline(self, page: Page):
        login_as_doctor(page)
        search_page = SearchPage(page)
        timeline_page = TimelinePage(page)
        
        with allure.step("Bước 1: Tìm kiếm bệnh nhân thành công"):
            search_page.search_cccd("012345678912")
            expect(search_page.patient_card).to_be_visible()
            
        with allure.step("Bước 2: Bấm nút 'Xem Timeline Bệnh Án'"):
            search_page.go_to_timeline()
            
        with allure.step("Bước 3: Kiểm tra chuyển hướng thành công sang trang timeline.html"):
            expect(page).to_have_url(re.compile(r".*timeline\.html.*"))
            expect(timeline_page.timeline_container).to_be_visible()
            allure.attach(page.screenshot(), name="Giao_Dien_Timeline_Benh_Nhan", attachment_type=allure.attachment_type.PNG)


    @allure.story("Thêm ca khám mới")
    @allure.title("TC_UI_08: Bác sĩ tạo ca khám mới điền thiếu trường bắt buộc")
    @pytest.mark.e2e
    @pytest.mark.boundary
    def test_tc_ui_08_doctor_add_record_missing_fields(self, page: Page):
        login_as_doctor(page)
        search_page = SearchPage(page)
        timeline_page = TimelinePage(page)
        
        with allure.step("Tiền quyết: Bác sĩ truy cập vào timeline của bệnh nhân"):
            search_page.search_cccd("012345678912")
            search_page.go_to_timeline()
            expect(timeline_page.banner_ma_bn).not_to_have_text("---")

        with allure.step("Bước 1: Mở form thêm ca khám"):
            timeline_page.btn_add_new_record.click()
            expect(timeline_page.record_modal).to_be_visible()

        with allure.step("Bước 2: Cố tình để trống trường 'Triệu chứng', chỉ điền 'Chẩn đoán'"):
            timeline_page.input_trieu_chung.fill("") 
            timeline_page.input_chan_doan.fill("Cảm cúm")
            timeline_page.btn_save_record.click()
            
        with allure.step("Bước 3: Kiểm tra trình duyệt chặn thao tác (HTML5 Validation)"):
            expect(timeline_page.input_trieu_chung).to_have_attribute("required", "")
            is_missing = timeline_page.input_trieu_chung.evaluate("node => node.validity.valueMissing")
            assert is_missing is True, "Trình duyệt không chặn lỗi bỏ trống trường bắt buộc!"
            allure.attach(page.screenshot(), name="Chan_Loi_Form_Rong", attachment_type=allure.attachment_type.PNG)


    @allure.story("Thêm ca khám mới")
    @allure.title("TC_UI_09: Bác sĩ tạo ca khám mới thành công với dữ liệu y tế thuần Việt ngẫu nhiên")
    @pytest.mark.e2e
    @pytest.mark.smoke
    @pytest.mark.happy_path
    def test_tc_ui_09_doctor_add_record_success(self, page: Page):
        login_as_doctor(page)
        search_page = SearchPage(page)
        timeline_page = TimelinePage(page)
        
        search_page.search_cccd("012345678912")
        search_page.go_to_timeline()
        
        with allure.step("Bước 1: Bác sĩ mở Modal thêm ca khám mới"):
            timeline_page.btn_add_new_record.click()
            expect(timeline_page.record_modal).to_be_visible()
            page.once("dialog", lambda dialog: dialog.accept())
        
        # Bốc ngẫu nhiên từ kho dữ liệu bằng Faker
        danh_sach_trieu_chung = ["Sốt cao kèm ho khan", "Đau đầu chóng mặt", "Đau tức ngực trái", "Đau bụng râm ran", "Đau mỏi vai gáy"]
        danh_sach_chan_doan = ["Viêm họng cấp", "Thiếu máu não", "Rối loạn tiêu hóa", "Mệt mỏi toàn thân", "Cảm cúm"]
        danh_sach_don_thuoc = ["Paracetamol 500g", "Omeprazole 20mg", "Vitamin C sủi", "Acetylcystein 200mg", "Thuốc giảm đau thông thường"]
        
        random_trieu_chung = fake.random_element(danh_sach_trieu_chung)
        random_chan_doan = fake.random_element(danh_sach_chan_doan)
        random_ghi_chu = fake.random_element(danh_sach_don_thuoc)
        
        with allure.step(f"Bước 2: Điền dữ liệu ngẫu nhiên (Triệu chứng: '{random_trieu_chung}')"):
            timeline_page.input_trieu_chung.fill(random_trieu_chung)
            timeline_page.input_chan_doan.fill(random_chan_doan)
            timeline_page.input_ghi_chu.fill(random_ghi_chu)
            allure.attach(page.screenshot(), name="Dien_Form_Tao_Ca_Kham", attachment_type=allure.attachment_type.PNG)
            
        with allure.step("Bước 3: Bấm 'Lưu ca khám' và kiểm tra dữ liệu hiển thị trên Timeline"):
            timeline_page.btn_save_record.click()
            expect(timeline_page.record_modal).not_to_be_visible()
            
            first_record = timeline_page.record_cards.first
            expect(first_record).to_be_visible()
            expect(first_record).to_contain_text(random_trieu_chung)
            allure.attach(page.screenshot(), name="Ket_Qua_Ca_Kham_Moi_Tren_Timeline", attachment_type=allure.attachment_type.PNG)