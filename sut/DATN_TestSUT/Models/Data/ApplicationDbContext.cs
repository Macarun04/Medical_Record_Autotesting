using DATN_TestSUT.Models; // Trỏ đúng vào thư mục chứa 4 file class của bạn
using Microsoft.EntityFrameworkCore;

namespace DATN_TestSUT.Models.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
        {
        }

        public DbSet<User> Users { get; set; }
        public DbSet<Patient> Patients { get; set; }
        public DbSet<Doctor> Doctors { get; set; }
        public DbSet<MedicalRecord> MedicalRecords { get; set; }
    }
}