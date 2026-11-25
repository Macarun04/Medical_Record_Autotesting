using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace DATN_TestSUT.Models
{
    [Table("Doctors")]
    public class Doctor
    {
        [Key]
        public string MaBacSi { get; set; }
        public string TenBacSi { get; set; }
        public string ChuyenKhoa { get; set; }
    }
}
