# Báo cáo Kết quả Đo lường Mốc 04: Độ bao phủ nhánh (Branch Coverage) và Độ ổn định (Flaky Rate)

## 1. Giao thức đo lường (Measurement Protocol)
* **Phạm vi kiểm thử:** 4 màn hình giao diện, 8 API nghiệp vụ, tổng cộng 50 test case đã đóng băng (40 API test + 10 E2E UI test).
* **Môi trường thực thi:** GitHub Actions (`ubuntu-latest`), Docker Compose (`docker-compose.ci.yml`), SQL Server 2022, .NET 10.0 (`DATN_TestSUT`), Python 3.12.16, PyTest + Playwright 1.49.0 (Chromium 131).
* **Commit tham chiếu:**
  * Dữ liệu 20 run liên tiếp: `8b0584bfc9e6032e32bb4424e069f1abc17c825c`
  * Dữ liệu Branch Coverage & lưu trữ bằng chứng trên nhánh `main`: `caea45c` (cập nhật đồng bộ tại `a8fede9`)
* **Lệnh thực thi thực nghiệm:**
  * Khởi chạy SUT có bật thu thập coverage trên container backend:
    `ENABLE_COVERAGE=true docker compose -f docker-compose.ci.yml up -d --build`
  * Chạy toàn bộ 50 test case (không cấu hình retry để phản ánh đúng độ ổn định thực tế):
    `pytest tests -v --alluredir=allure-results`
  * Xuất báo cáo Cobertura XML từ tiến trình backend và sinh biểu đồ:
    `dotnet-coverage collect -f cobertura -o /coverage/coverage.xml dotnet DATN_TestSUT.dll`
    `python scripts/generate_coverage_chart.py evidence/metrics/coverage.xml evidence/metrics/coverage-chart.png`

---

## 2. Kết quả đo Branch Coverage (Backend SUT - `DATN_TestSUT`)
* **Tệp bằng chứng:** `evidence/metrics/coverage.xml`, `evidence/metrics/coverage-chart.png`
* **Kết quả tổng hợp:**
  * **Branch Coverage:** **84,75%** (`100 / 118` nhánh điều kiện được thực thi) — **Đạt** (vượt ngưỡng cam kết `≥ 70%` là `+14,75%`).
  * **Line Coverage:** **94,42%** (`237 / 251` dòng lệnh được thực thi).

| Thành phần (`Class` / `Controller`) | Branch Coverage | Line Coverage | Số nhánh phủ / Tổng nhánh | Ghi chú nhánh chưa phủ |
| :--- | :---: | :---: | :---: | :--- |
| `AuthController` | 91,67% | 96,15% | 11 / 12 | Nhánh xử lý ngoại lệ trạng thái phụ (dòng 54) |
| `PatientsController` | 88,24% | 96,15% | 30 / 34 | Các nhánh rẽ điều kiện lọc phụ (dòng 25, 87, 119) |
| `DoctorsController` | 83,33% | 95,45% | 20 / 24 | Nhánh điều kiện phụ khi truy vấn/tạo bác sĩ (dòng 29, 65) |
| `TimelineController` | 77,78% | 94,44% | 14 / 18 | Tổ hợp nhiều tham số lọc đồng thời (dòng 55) & bắt lỗi phòng thủ (dòng 82, 111) |
| `Program` & `ApplicationDbContext` | 90,00% | 94,83% | 25 / 30 | Nhánh cấu hình dự phòng môi trường phát triển (`IsDevelopment`) |
| **Tổng cộng (`DATN_TestSUT`)** | **84,75%** | **94,42%** | **100 / 118** | **Đạt ngưỡng cam kết `≥ 70%`** |

---

## 3. Kết quả đo Flaky Rate qua 20 lần chạy CI liên tiếp
* **Tệp bằng chứng:** `evidence/metrics/runs-20-summary.csv`, `evidence/metrics/flaky-20.csv`
* **Kết quả tổng hợp:**
  * **Tổng số run:** 20 run liên tiếp trên cùng Commit SHA `8b0584b` (`20/20` run đạt trạng thái `PASS`).
  * **Tổng số lượt thực thi ở cấp test case:** `50 test cases × 20 runs = 1.000 lượt`.
  * **Số lượt thực thi không nhất quán (Flaky):** `0 / 1.000` lượt (**Flaky rate = 0,00%**) — **Đạt** (thấp hơn ngưỡng tối đa cho phép `< 2%`, tức `< 20 / 1.000` lượt).
  * **Thời gian thực thi PyTest trung bình:** `9,45 giây/run` (dao động từ `8,54s` đến `10,82s`).
  * **Danh sách test case flaky:** `0` test case (100% test case đạt trạng thái `PASS` nhất quán qua cả 20 lần chạy).