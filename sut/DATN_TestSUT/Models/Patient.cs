using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace DATN_TestSUT.Models
{
    [Table("Patients")]
    public class Patient
    {
        [Key]
        public string MaBenhNhan { get; set; }
        public string SoCCCD { get; set; }
        public string HoVaTen { get; set; }
        public DateTime NgaySinh { get; set; }
        public string GioiTinh { get; set; }
        public string Sdt { get; set; }
        public string DiaChi { get; set; }
    }
}