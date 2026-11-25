using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace DATN_TestSUT.Models.Data // (hoặc namespace hiện tại của bạn)
{
    [Table("Users")]
    public class User
    {
        [Key]
        public string TenDangNhap { get; set; }
        public string MatKhau { get; set; }
        public string VaiTro { get; set; }

        // Thêm dấu ? vào đây để cho phép NULL
        public string? MaBacSi { get; set; }
        public string? MaBenhNhan { get; set; }
    }
}