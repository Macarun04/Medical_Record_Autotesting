using Microsoft.AspNetCore.Mvc;
using System.Linq;
using DATN_TestSUT.Models;
using DATN_TestSUT.Models.Data;

namespace DATN_TestSUT.Controllers
{
    [Route("api/v1/auth")]
    [ApiController]
    public class AuthController : ControllerBase
    {
        // Inject DbContext (đại diện cho Database của bạn)
        private readonly ApplicationDbContext _context;

        public AuthController(ApplicationDbContext context) 
        {
            _context = context;
        }

        [HttpPost("login")]
        public IActionResult Login([FromBody] LoginRequest request)
        {
            // Xử lý TC_API1_04 & TC_API1_05: Bỏ trống dữ liệu hoặc sai định dạng
            if (request == null || string.IsNullOrWhiteSpace(request.TenDangNhap) || string.IsNullOrWhiteSpace(request.MatKhau))
            {
                return BadRequest(new { message = "Thiếu thông tin đăng nhập." });
            }

            // Truy vấn vào bảng Users theo tenDangNhap và matKhau
            var user = _context.Users.FirstOrDefault(u =>
                u.TenDangNhap == request.TenDangNhap &&
                u.MatKhau == request.MatKhau);

            // Xử lý TC_API1_03: Trả về 401 nếu sai tài khoản/mật khẩu
            if (user == null)
            {
                return Unauthorized(new { message = "Sai tài khoản hoặc mật khẩu" });
            }

            // Xử lý TC_API1_01 & TC_API1_02: Trả về 200 OK kèm thông tin phân quyền
            // (Trong dự án thực tế, bạn sẽ dùng JwtSecurityTokenHandler để sinh mã JWT thật tại đây)
            string mockJwtToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.MockTokenForTesting...";

            if (user.VaiTro == "Bác sĩ")
            {
                return Ok(new
                {
                    token = mockJwtToken,
                    vaiTro = user.VaiTro,
                    maBacSi = user.MaBacSi
                });
            }

            if (user.VaiTro == "Bệnh nhân")
            {
                return Ok(new
                {
                    token = mockJwtToken,
                    vaiTro = user.VaiTro,
                    maBenhNhan = user.MaBenhNhan
                });
            }

            return BadRequest(new { message = "Lỗi hệ thống: Phân quyền không hợp lệ." });
        }
    }

    // Class DTO (Data Transfer Object) để hứng dữ liệu JSON từ Pytest
    public class LoginRequest
    {
        public string TenDangNhap { get; set; }
        public string MatKhau { get; set; }
    }
}