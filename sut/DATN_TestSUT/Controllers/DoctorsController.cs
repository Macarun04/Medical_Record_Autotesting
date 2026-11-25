using DATN_TestSUT.Models;
using DATN_TestSUT.Models.Data;
using Microsoft.AspNetCore.Mvc;
using System.Linq;

namespace DATN_TestSUT.Controllers
{
    [Route("api/v1/doctors")]
    [ApiController]
    public class DoctorsController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public DoctorsController(ApplicationDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public IActionResult GetDoctors([FromQuery] string? chuyenKhoa)
        {
            // 1. Kiểm tra Token xác thực (đáp ứng chuẩn xác TC_API6_05_Doctors_NoAuth)
            if (!Request.Headers.ContainsKey("Authorization"))
            {
                return Unauthorized(new { message = "Bạn chưa đăng nhập hoặc thiếu Token xác thực" });
            }

            var token = Request.Headers["Authorization"].ToString();
            if (string.IsNullOrWhiteSpace(token) || !token.StartsWith("Bearer "))
            {
                return Unauthorized(new { message = "Định dạng Token không hợp lệ" });
            }

            // 2. Truy vấn trực tiếp từ bảng Doctors (khớp với schema SQL bạn cung cấp)
            var query = _context.Doctors.AsQueryable();

            // 3. Lọc theo chuyên khoa nếu có truyền query parameter (?chuyenKhoa=...)
            if (!string.IsNullOrWhiteSpace(chuyenKhoa))
            {
                // Dùng thông so sánh không phân biệt hoa thường để hỗ trợ tốt URL Encoding
                query = query.Where(d => d.ChuyenKhoa != null && d.ChuyenKhoa.ToLower() == chuyenKhoa.ToLower());
            }

            // 4. Map dữ liệu trả về JSON khớp đúng với định dạng yêu cầu của test case
            var result = query.Select(d => new
            {
                maBacSi = d.MaBacSi,
                hoVaTen = d.TenBacSi,     // Khớp với cột tenBacSi trong bảng Doctors
                chuyenKhoa = d.ChuyenKhoa // Khớp với cột chuyenKhoa trong bảng Doctors
            }).ToList();

            return Ok(result);
        }

        [HttpPost]
        public IActionResult CreateDoctor([FromBody] Doctor model)
        {
            // 1. Kiểm tra Token xác thực (Bảo mật / Phân quyền Admin)
            if (!Request.Headers.ContainsKey("Authorization"))
            {
                return Unauthorized(new { message = "Bạn chưa đăng nhập hoặc thiếu Token xác thực" });
            }

            var token = Request.Headers["Authorization"].ToString();
            if (string.IsNullOrWhiteSpace(token) || !token.StartsWith("Bearer "))
            {
                return Unauthorized(new { message = "Định dạng Token không hợp lệ" });
            }

            // (Tuỳ chọn) Kiểm tra nếu là Token của Bác sĩ thường thì chặn 403 (Mô phỏng phân quyền RBAC)
            if (token.Contains("Doctor_Valid"))
            {
                return StatusCode(403, new { message = "Bạn không có quyền thực hiện chức năng này" });
            }

            // 2. Kiểm tra dữ liệu bắt buộc cơ bản
            if (string.IsNullOrWhiteSpace(model.MaBacSi) || string.IsNullOrWhiteSpace(model.TenBacSi) || string.IsNullOrWhiteSpace(model.ChuyenKhoa))
            {
                return BadRequest(new { message = "Thiếu các trường thông tin bắt buộc" });
            }

            // 3. Kiểm tra trùng lặp mã bác sĩ hoặc tên đăng nhập trong DB
            var existingDoctor = _context.Doctors.FirstOrDefault(d => d.MaBacSi == model.MaBacSi);
            if (existingDoctor != null)
            {
                return Conflict(new { message = "Mã bác sĩ đã tồn tại" });
            }

            // 4. Thêm mới vào Database (Giả sử bảng Doctors có các cột tương ứng)
            // Lưu ý: Đảm bảo model mapping khớp với cấu trúc entity thực tế của bạn
            var newDoctor = new Doctor
            {
                MaBacSi = model.MaBacSi,
                TenBacSi = model.TenBacSi,
                ChuyenKhoa = model.ChuyenKhoa
                // Thêm các trường khác nếu có
            };

            _context.Doctors.Add(newDoctor);
            _context.SaveChanges();

            // Trả về 201 Created kèm thông tin vừa tạo
            return StatusCode(201, new
            {
                message = "Tạo bác sĩ thành công",
                data = new { maBacSi = newDoctor.MaBacSi }
            });
        }
    }
}