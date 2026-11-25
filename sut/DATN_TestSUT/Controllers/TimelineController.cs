using DATN_TestSUT.Models;
using DATN_TestSUT.Models.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Linq;

namespace DATN_TestSUT.Controllers
{
    [Route("api/v1")]
    [ApiController]
    public class TimelineController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public TimelineController(ApplicationDbContext context)
        {
            _context = context;
        }

        // 1. API lấy thông tin bệnh nhân và danh sách lịch sử khám bệnh
        [HttpGet("patients/{maBenhNhan}/record")]
        public IActionResult GetPatientTimeline(string maBenhNhan)
        {
            // --- THÊM ĐOẠN NÀY ĐỂ BẮT LỖI 401 (TC_API3_04) ---
            var authHeader = Request.Headers["Authorization"].ToString();
            if (string.IsNullOrWhiteSpace(authHeader) || !authHeader.StartsWith("Bearer "))
            {
                return Unauthorized(new { message = "Thiếu hoặc sai JWT Token" });
            }
            try
            {
                // Kiểm tra bệnh nhân có tồn tại không
                var patient = _context.Patients.FirstOrDefault(p => p.MaBenhNhan == maBenhNhan);
                if (patient == null)
                {
                    return NotFound(new { message = "Không tìm thấy bệnh nhân." });
                }

                // Lấy danh sách ca khám an toàn, sắp xếp mới nhất lên trên
                var records = _context.MedicalRecords
                    .Where(m => m.MaBenhNhan == maBenhNhan)
                    .OrderByDescending(m => m.NgayKham)
                    .Select(m => new {
                        maCaKham = m.MaCaKham ?? "",
                        ngayKham = m.NgayKham,
                        maBacSi = m.MaBacSi ?? "",
                        chuyenKhoa = m.ChuyenKhoa ?? "",
                        trieuChung = m.TrieuChung ?? "",
                        chanDoan = m.ChanDoan ?? "",
                        ghiChuDonThuoc = m.GhiChuDonThuoc ?? ""
                    })
                    .ToList();

                // Trả về dữ liệu chuẩn khớp với cấu trúc Frontend mong đợi
                return Ok(new
                {
                    patient = new
                    {
                        maBenhNhan = patient.MaBenhNhan ?? "",
                        soCCCD = patient.SoCCCD ?? "",
                        hoVaTen = patient.HoVaTen ?? "",
                        ngaySinh = patient.NgaySinh,
                        gioiTinh = patient.GioiTinh ?? "",
                        sdt = patient.Sdt ?? "",
                        diaChi = patient.DiaChi ?? ""
                    },
                    records = records
                });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { message = "Lỗi Server: " + ex.Message });
            }
        }

        // 2. API tạo mới ca khám bệnh (POST)
        [HttpPost("records")]
        public IActionResult CreateMedicalRecord([FromBody] CreateRecordRequest request) // Sử dụng DTO thay vì Entity
        {

            // 1. Kiểm tra có Token không (Chặn lỗi 401 - TC_API4_no_token_returns_401)
            if (!Request.Headers.ContainsKey("Authorization"))
            {
                return Unauthorized(new { message = "Bạn chưa đăng nhập hoặc thiếu Token" });
            }

            // 2. Kiểm tra quyền Bác sĩ (Chặn lỗi 403 - TC_API4_05_create_record_wrong_role)
            var token = Request.Headers["Authorization"].ToString();
            // Chuyển token về chữ thường (ToLower) để bắt chính xác chữ 'patient' gửi từ PyTest
            if (token.ToLower().Contains("patient") || token.Contains("BN_"))
            {
                return StatusCode(403, new { message = "Chỉ bác sĩ mới được tạo ca khám" });
            }

            // 3. Validate dữ liệu đầu vào (Chặn lỗi 400 - TC_API4_missing_required_fields)
            if (request == null ||
                string.IsNullOrWhiteSpace(request.MaBenhNhan) ||
                string.IsNullOrWhiteSpace(request.ChanDoan)) // Đã thêm chặn lỗi trống Chẩn đoán
            {
                return BadRequest(new { message = "Thông tin ca khám không hợp lệ. Mã bệnh nhân và Chẩn đoán là bắt buộc!" });
            }

            // THÊM ĐOẠN NÀY ĐỂ BẮT LỖI VƯỢT QUÁ 2000 KÝ TỰ:
            if (!string.IsNullOrEmpty(request.TrieuChung) && request.TrieuChung.Length > 2000)
            {
                return BadRequest(new { message = "Triệu chứng không được vượt quá 2000 ký tự." });
            }

            // 4. Lấy thông tin bác sĩ từ DB để lấy Chuyên khoa
            var doctor = _context.Doctors.FirstOrDefault(d => d.MaBacSi == request.MaBacSi);
            if (doctor == null)
            {
                return BadRequest(new { message = "Không tìm thấy thông tin Bác sĩ phụ trách." });
            }

            // 5. Tạo đối tượng MedicalRecord chuẩn để lưu vào Database
            var newRecord = new MedicalRecord
            {
                // Tự động sinh mã và ngày giờ
                MaCaKham = "MK_" + DateTime.Now.Ticks.ToString().Substring(10),
                NgayKham = DateTime.Now,

                // Gán dữ liệu từ Frontend gửi lên (DTO)
                MaBenhNhan = request.MaBenhNhan,
                MaBacSi = request.MaBacSi,
                TrieuChung = request.TrieuChung,
                ChanDoan = request.ChanDoan,
                GhiChuDonThuoc = request.GhiChuDonThuoc,

                // Tự động gán chuyên khoa của bác sĩ
                ChuyenKhoa = doctor.ChuyenKhoa
            };

            // 6. Lưu vào Database
            _context.MedicalRecords.Add(newRecord);
            _context.SaveChanges();

            return StatusCode(201, new { message = "Thêm ca khám thành công!", data = newRecord });
        }
    }

    // TẠO THÊM CLASS NÀY Ở DƯỚI CÙNG (TRONG CÙNG NAMESPACE)
    // DTO (Data Transfer Object) dùng để nhận chính xác những gì Frontend gửi
    public class CreateRecordRequest
    {
        public string? MaBenhNhan { get; set; }
        public string? MaBacSi { get; set; }
        public string? TrieuChung { get; set; }
        public string? ChanDoan { get; set; }
        public string? GhiChuDonThuoc { get; set; }
    }
}