using DATN_TestSUT.Models;
using DATN_TestSUT.Models.Data;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Linq;

namespace DATN_TestSUT.Controllers
{
    [Route("api/v1/patients")]
    [ApiController]
    public class PatientsController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public PatientsController(ApplicationDbContext context)
        {
            _context = context;
        }

        // API 2: Tra cứu hồ sơ qua CCCD (GET)
        [HttpGet("search")]
        public IActionResult SearchPatient([FromQuery] string cccd)
        {
            // 1. Kiểm thử bảo mật: Fake Auth Check (Chặn lỗi 401)
            if (!Request.Headers.ContainsKey("Authorization"))
            {
                return Unauthorized(new { message = "Bạn chưa đăng nhập hoặc thiếu Token" });
            }
            // Kiểm tra đầu vào
            // Thêm block kiểm tra biên này để ném lỗi 400 (Bad Request)
            if (string.IsNullOrEmpty(cccd) || cccd.Length != 12 || !cccd.All(char.IsDigit))
            {
                return BadRequest(new { message = "Số CCCD không đúng định dạng" });
            }

            // Tìm kiếm trong Database
            var patient = _context.Patients.FirstOrDefault(p => p.SoCCCD == cccd);

            // Nếu không có ai
            if (patient == null)
            {
                return NotFound(new { message = "Không tìm thấy hồ sơ bệnh nhân" });
            }

            // Nếu tìm thấy, trả về thông tin (HTTP 200 OK)
            return Ok(patient);
        }

        // API 5: Tạo mới bệnh nhân (POST)
        // Tạo một Class DTO nhỏ để hứng dữ liệu từ Python/Form (để dưới cùng file hoặc trong namespace)
        public class CreatePatientRequest
        {
            public string? SoCCCD { get; set; }
            public string? HoVaTen { get; set; }
            public DateTime NgaySinh { get; set; }
            public string? GioiTinh { get; set; }
            public string Sdt { get; set; }
            public string DiaChi { get; set; }
        }

        // API 5: Tạo mới bệnh nhân (POST)
        [HttpPost]
        public IActionResult CreatePatient([FromBody] CreatePatientRequest request) // <--- Đổi Patient thành CreatePatientRequest
        {
            // Bắt lỗi 400: Thiếu thông tin bắt buộc
            if (string.IsNullOrWhiteSpace(request.SoCCCD) ||
                string.IsNullOrWhiteSpace(request.HoVaTen) ||
                request.NgaySinh == default ||
                string.IsNullOrWhiteSpace(request.Sdt) ||       // Thêm điều kiện này
                string.IsNullOrWhiteSpace(request.DiaChi))      // Thêm điều kiện này
            {
                return BadRequest(new { message = "Thiếu thông tin bắt buộc (CCCD, Họ tên, Ngày sinh, SĐT, Địa chỉ)." });
            }

            // Bắt lỗi 409: Trùng lặp số CCCD
            bool isExist = _context.Patients.Any(p => p.SoCCCD == request.SoCCCD);
            if (isExist)
            {
                return StatusCode(409, new { message = "Số CCCD đã tồn tại trong hệ thống." });
            }

            // Tự động sinh Mã bệnh nhân (VD: BN_142530)
            Random rand = new Random();
            string newMaBenhNhan = "BN_" + DateTime.Now.ToString("HHmmssfff") + rand.Next(10, 99);

            // Tạo đối tượng Patient thực thụ để lưu vào Database
            var newPatient = new Patient
            {
                MaBenhNhan = newMaBenhNhan,
                SoCCCD = request.SoCCCD,
                HoVaTen = request.HoVaTen,
                NgaySinh = request.NgaySinh,
                GioiTinh = string.IsNullOrWhiteSpace(request.GioiTinh) ? "Khác" : request.GioiTinh,
                Sdt = request.Sdt,
                DiaChi = request.DiaChi,
            };

            _context.Patients.Add(newPatient);
            _context.SaveChanges();

            return Created("", new
            {
                maBenhNhan = newMaBenhNhan,
                message = "Tạo hồ sơ bệnh nhân thành công"
            });
        }

        // API 8: Lấy toàn bộ danh sách bệnh nhân hoặc lọc tìm kiếm (GET)
        [HttpGet]
        public IActionResult GetAllPatients([FromQuery] string? search)
        {
            // 1. Kiểm tra Token xác thực (đáp ứng TC_API8_05_get_patients_no_auth)
            if (!Request.Headers.ContainsKey("Authorization"))
            {
                return Unauthorized(new { message = "Bạn chưa đăng nhập hoặc thiếu Token xác thực" });
            }

            var token = Request.Headers["Authorization"].ToString();
            if (string.IsNullOrWhiteSpace(token) || !token.StartsWith("Bearer "))
            {
                return Unauthorized(new { message = "Định dạng Token không hợp lệ" });
            }

            // 2. Phân quyền RBAC (đáp ứng TC_API8_04_get_patients_wrong_role)
            // Nếu dùng Token của Bệnh nhân thì không được phép xem danh sách toàn viện -> Trả về 403 Forbidden
            if (token.Contains("Patient_"))
            {
                return StatusCode(403, new { message = "Bạn không có quyền xem danh sách bệnh nhân toàn viện" });
            }

            // 3. Truy vấn danh sách từ Database
            var query = _context.Patients.AsQueryable();

            // Hỗ trợ lọc tìm kiếm (phục vụ TC_API8_02_get_patients_empty)
            if (!string.IsNullOrWhiteSpace(search))
            {
                query = query.Where(p => (p.HoVaTen != null && p.HoVaTen.Contains(search)) ||
                                         (p.SoCCCD != null && p.SoCCCD.Contains(search)));
            }

            var result = query.ToList();

            // Trả về HTTP 200 OK kèm danh sách
            return Ok(result);
        }
    }
}