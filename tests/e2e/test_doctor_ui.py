import pytest
import re
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage

def login_as_doctor(page: Page):
    """Hàm hỗ trợ: Đăng nhập sẵn vào tài khoản Bác sĩ trước khi test nghiệp vụ"""
    login_page = LoginPage(page)
    login_page.open()
    page.once("dialog", lambda dialog: dialog.accept())
    # Sử dụng thông tin đăng nhập đúng chuẩn từ bảng Users của bạn
    login_page.login("BS_NguyenVanA", "Password123!")
    expect(page).to_have_url(re.compile(r".*search\.html"))

@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.happy_path
def test_tc_ui_05_doctor_search_patient_success(page: Page):
    """TC_UI_05: Bác sĩ tra cứu CCCD thành công"""
    login_as_doctor(page)
    
    # 1. Nhập số CCCD hợp lệ. Dùng ID thực tế 'searchInput' từ search.html
    cccd_input = page.locator("input#searchInput") 
    
    # LƯU Ý CHO BẠN: Thay '012345678912' bằng 1 số CCCD đã có trong bảng Patients (DB của bạn)
    cccd_input.fill("012345678912") 
    
    # 2. Ấn phím Enter
    cccd_input.press("Enter")
    
    # Kết quả mong đợi: Hiển thị chi tiết hồ sơ bệnh nhân (ID thực tế là 'patientCard')
    patient_card = page.locator("#patientCard")
    expect(patient_card).to_be_visible()
    
    # Kiểm tra các trường dữ liệu phải được render ra
    expect(page.locator("#valMaBN")).not_to_have_text("---")
    expect(page.locator("#valCCCD")).not_to_have_text("---")
    expect(page.locator("#valHoTen")).not_to_have_text("---")

@pytest.mark.e2e
@pytest.mark.error_path
def test_tc_ui_06_doctor_search_not_found(page: Page):
    """TC_UI_06: Bác sĩ tra cứu CCCD không có thật (đủ 12 số)"""
    login_as_doctor(page)
    
    # 1. Nhập một số CCCD đủ 12 số nhưng không có thật
    cccd_input = page.locator("input#searchInput")
    cccd_input.fill("999999999999")
    
    # 2. Ấn phím Enter
    cccd_input.press("Enter")
    
    # Kết quả mong đợi: Thông báo lỗi xuất hiện
    error_msg = page.locator("#errorMessage")
    expect(error_msg).to_be_visible()
    expect(error_msg).to_have_text("Không tìm thấy hồ sơ bệnh nhân với số CCCD này!")

@pytest.mark.e2e
@pytest.mark.happy_path
def test_tc_ui_07_doctor_view_timeline(page: Page):
    """TC_UI_07: Bác sĩ xem lịch sử ca khám của bệnh nhân (timeline)"""
    login_as_doctor(page)
    
    # Tiền quyết: Tìm thấy bệnh nhân trước
    page.locator("input#searchInput").fill("012345678912") # Đổi CCCD này cho khớp DB
    page.locator("input#searchInput").press("Enter")
    expect(page.locator("#patientCard")).to_be_visible()
    
    # 1. Bấm chọn "Xem Timeline Bệnh Án"
    page.locator("button#btnGoTimeline").click()
    
    # Kết quả mong đợi: Chuyển hướng sang giao diện Timeline
    expect(page).to_have_url(re.compile(r".*timeline\.html.*"))
    
    # Kiểm tra danh sách hiển thị
    timeline_container = page.locator("#timelineContainer")
    expect(timeline_container).to_be_visible()

@pytest.mark.e2e
@pytest.mark.boundary
def test_tc_ui_08_doctor_add_record_missing_fields(page: Page):
    """TC_UI_08: Bác sĩ tạo ca khám mới điền thiếu trường bắt buộc"""
    login_as_doctor(page)
    
    # --- THAY THẾ LỆNH page.goto BẰNG THAO TÁC UI ---
    # 1. Tìm bệnh nhân hợp lệ (Lưu ý: Thay CCCD này bằng số thực tế trong DB)
    page.locator("input#searchInput").fill("012345678912") 
    page.locator("input#searchInput").press("Enter")
    expect(page.locator("#patientCard")).to_be_visible()
    
    # 2. Bấm chuyển sang Timeline
    page.locator("button#btnGoTimeline").click()
    expect(page.locator("#bannerMaBN")).not_to_have_text("---")
    # ------------------------------------------------

    # Mở form thêm ca khám
    page.locator("button#btnAddRecord").click()
    expect(page.locator("#recordModal")).to_be_visible()

    # 1. Để trống "Triệu chứng", điền "Chẩn đoán"
    symptom_input = page.locator("textarea#inputTrieuChung")
    diagnosis_input = page.locator("textarea#inputChanDoan")
    
    symptom_input.fill("") 
    diagnosis_input.fill("Cảm cúm")
    
    # 2. Bấm nút lưu dữ liệu
    page.locator("button.btn-save").click()
    
    # Kết quả mong đợi: HTML5 Validation chặn submit
    expect(symptom_input).to_have_attribute("required", "")
    
    # Xác nhận trạng thái báo lỗi bỏ trống
    is_missing = symptom_input.evaluate("node => node.validity.valueMissing")
    assert is_missing is True, "Trình duyệt không chặn lỗi bỏ trống trường bắt buộc!"

@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.happy_path
def test_tc_ui_09_doctor_add_record_success(page: Page):
    """TC_UI_09: Bác sĩ tạo ca khám mới thành công"""
    login_as_doctor(page)
    
    # --- THAY THẾ LỆNH page.goto BẰNG THAO TÁC UI ---
    page.locator("input#searchInput").fill("012345678912") 
    page.locator("input#searchInput").press("Enter")
    expect(page.locator("#patientCard")).to_be_visible()
    page.locator("button#btnGoTimeline").click()
    expect(page.locator("#bannerMaBN")).not_to_have_text("---")
    # ------------------------------------------------
    
    # 1. Bấm nút "Thêm ca khám mới"
    page.locator("button#btnAddRecord").click()
    expect(page.locator("#recordModal")).to_be_visible()
    
    # Xử lý Alert "Thêm ca khám thành công!" trước khi nó bật ra
    page.once("dialog", lambda dialog: dialog.accept())
    
    # 2. Điền đầy đủ thông tin
    page.locator("textarea#inputTrieuChung").fill("Sốt, ho")
    page.locator("textarea#inputChanDoan").fill("Viêm họng")
    page.locator("textarea#inputGhiChu").fill("Nghỉ ngơi")
    
    # 3. Bấm "Lưu ca khám"
    page.locator("button.btn-save").click()
    
    # Kết quả mong đợi: Modal ẩn đi, danh sách reload và chứa bản ghi mới
    expect(page.locator("#recordModal")).not_to_be_visible()
    
    first_record = page.locator(".record-card").first
    expect(first_record).to_be_visible()
    expect(first_record).to_contain_text("Sốt, ho")