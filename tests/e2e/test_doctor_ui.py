import re
import pytest
from faker import Faker
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from pages.timeline_page import TimelinePage

fake = Faker("vi_VN")
SAMPLE_PATIENT_CCCD = "012345678912"


def login_as_doctor(page: Page):
    """Hàm hỗ trợ: Đăng nhập sẵn vào tài khoản Bác sĩ trước khi test nghiệp vụ."""
    login_page = LoginPage(page)
    login_page.open()
    page.once("dialog", lambda dialog: dialog.accept())
    login_page.login("BS_NguyenVanA", "Password123!")
    expect(page).to_have_url(re.compile(r".*search\.html"), timeout=15000)


@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.happy_path
def test_tc_ui_05_doctor_search_patient_success(page: Page):
    """TC_UI_05: Bác sĩ tra cứu CCCD thành công."""
    login_as_doctor(page)
    search_page = SearchPage(page)

    search_page.search_cccd(SAMPLE_PATIENT_CCCD)

    expect(search_page.patient_card).to_be_visible(timeout=15000)
    expect(search_page.val_ma_bn).not_to_have_text("---")
    expect(search_page.val_cccd).not_to_have_text("---")
    expect(search_page.val_hoten).not_to_have_text("---")


@pytest.mark.e2e
@pytest.mark.error_path
def test_tc_ui_06_doctor_search_not_found(page: Page):
    """TC_UI_06: Bác sĩ tra cứu CCCD không có thật (đủ 12 số)."""
    login_as_doctor(page)
    search_page = SearchPage(page)

    search_page.search_cccd("999999999999")

    expect(search_page.error_message).to_be_visible(timeout=15000)
    expect(search_page.error_message).to_have_text("Không tìm thấy hồ sơ bệnh nhân với số CCCD này!")


@pytest.mark.e2e
@pytest.mark.happy_path
def test_tc_ui_07_doctor_view_timeline(page: Page):
    """TC_UI_07: Bác sĩ xem lịch sử ca khám của bệnh nhân (timeline)."""
    login_as_doctor(page)
    search_page = SearchPage(page)
    timeline_page = TimelinePage(page)

    search_page.search_cccd(SAMPLE_PATIENT_CCCD)
    expect(search_page.patient_card).to_be_visible(timeout=15000)

    search_page.go_to_timeline()

    expect(page).to_have_url(re.compile(r".*timeline\.html.*"), timeout=15000)
    expect(timeline_page.timeline_container).to_be_visible()


@pytest.mark.e2e
@pytest.mark.boundary
def test_tc_ui_08_doctor_add_record_missing_fields(page: Page):
    """TC_UI_08: Bác sĩ tạo ca khám mới điền thiếu trường bắt buộc."""
    login_as_doctor(page)
    search_page = SearchPage(page)
    timeline_page = TimelinePage(page)

    search_page.search_cccd(SAMPLE_PATIENT_CCCD)
    expect(search_page.patient_card).to_be_visible(timeout=15000)
    search_page.go_to_timeline()
    expect(timeline_page.banner_ma_bn).not_to_have_text("---")

    timeline_page.btn_add_new_record.click()
    expect(timeline_page.record_modal).to_be_visible()

    timeline_page.input_trieu_chung.fill("")
    timeline_page.input_chan_doan.fill("Cảm cúm")
    timeline_page.btn_save_record.click()

    expect(timeline_page.input_trieu_chung).to_have_attribute("required", "")
    is_missing = timeline_page.input_trieu_chung.evaluate("node => node.validity.valueMissing")
    assert is_missing is True, "Trình duyệt không chặn lỗi bỏ trống trường bắt buộc!"


@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.happy_path
def test_tc_ui_09_doctor_add_record_success(page: Page):
    """TC_UI_09: Bác sĩ tạo ca khám mới thành công với dữ liệu y tế thuần Việt ngẫu nhiên."""
    login_as_doctor(page)
    search_page = SearchPage(page)
    timeline_page = TimelinePage(page)

    search_page.search_cccd(SAMPLE_PATIENT_CCCD)
    expect(search_page.patient_card).to_be_visible(timeout=15000)
    search_page.go_to_timeline()

    timeline_page.btn_add_new_record.click()
    expect(timeline_page.record_modal).to_be_visible()

    page.once("dialog", lambda dialog: dialog.accept())

    danh_sach_trieu_chung = [
        "Sốt cao kèm ho khan, đau rát họng",
        "Đau đầu chóng mặt, mệt mỏi kéo dài 2 ngày",
        "Đau tức ngực trái, khó thở nhẹ khi vận động",
        "Đau bụng râm ran vùng thượng vị, buồn nôn",
        "Đau mỏi vai gáy, tê tay trái",
    ]
    danh_sach_chan_doan = [
        "Viêm họng cấp do virus",
        "Thiếu máu não thoáng qua",
        "Rối loạn tiêu hóa / Viêm dạ dày nhẹ",
        "Hội chứng mệt mỏi toàn thân",
        "Cảm cúm thông thường",
    ]
    danh_sach_don_thuoc = [
        "Paracetamol 500g (ngày uống 2 viên chia sáng chiều), nghỉ ngơi nhiều.",
        "Omeprazole 20mg, uống trước ăn sáng 30 phút kết hợp men tiêu hóa.",
        "Vitamin C sủi, bổ sung nước điện giải, hạn chế thức khuya.",
        "Acetylcystein 200mg (long đờm), nhỏ mũi nước muối sinh lý.",
        "Thuốc giảm đau thông thường, tái khám sau 5 ngày nếu không đỡ.",
    ]

    random_trieu_chung = fake.random_element(danh_sach_trieu_chung)
    random_chan_doan = fake.random_element(danh_sach_chan_doan)
    random_ghi_chu = fake.random_element(danh_sach_don_thuoc)

    timeline_page.input_trieu_chung.fill(random_trieu_chung)
    timeline_page.input_chan_doan.fill(random_chan_doan)
    timeline_page.input_ghi_chu.fill(random_ghi_chu)

    timeline_page.btn_save_record.click()

    expect(timeline_page.record_modal).not_to_be_visible(timeout=15000)
    first_record = timeline_page.record_cards.first
    expect(first_record).to_be_visible(timeout=15000)
    expect(first_record).to_contain_text(random_trieu_chung)