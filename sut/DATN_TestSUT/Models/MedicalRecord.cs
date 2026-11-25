using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace DATN_TestSUT.Models
{
    [Table("MedicalRecords")]
    public class MedicalRecord
    {
        [Key]
        public string MaCaKham { get; set; }
        public string MaBenhNhan { get; set; }
        public string MaBacSi { get; set; }
        public DateTime NgayKham { get; set; }
        public string? ChuyenKhoa { get; set; }
        public string? TrieuChung { get; set; }
        public string? ChanDoan { get; set; }
        public string? GhiChuDonThuoc { get; set; }
    }
}