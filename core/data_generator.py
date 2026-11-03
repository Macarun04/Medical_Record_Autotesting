from faker import Faker
import random

# Khởi tạo Faker với bộ dữ liệu chuẩn Tiếng Việt
fake = Faker('vi_VN')

def generate_patient_data():
    """Sinh dữ liệu bệnh nhân mới ngẫu nhiên và chuẩn định dạng"""
    return {
        # CCCD Việt Nam có 12 số
        "soCCCD": str(fake.random_number(digits=12, fix_len=True)),
        "hoVaTen": fake.name(),
        # Ép định dạng ngày sinh YYYY-MM-DD
        "ngaySinh": fake.date_of_birth(minimum_age=1, maximum_age=90).strftime('%Y-%m-%d'),
        "gioiTinh": random.choice(["Nam", "Nữ"]),
        # Số điện thoại VN 10 số, bắt đầu bằng 0
        "sdt": "0" + str(fake.random_number(digits=9, fix_len=True)),
        "diaChi": fake.address()
    }

def generate_medical_record_data(ma_benh_nhan, ma_bac_si):
    """Sinh dữ liệu ca khám mới hợp lệ"""
    symptoms = ["Ho khan, sốt nhẹ", "Đau đầu, chóng mặt", "Đau dạ dày", "Khó thở, tức ngực", "Dị ứng ngoài da"]
    diagnoses = ["Viêm họng cấp", "Rối loạn tiền đình", "Viêm loét dạ dày", "Viêm phế quản", "Viêm da cơ địa"]
    
    return {
        "maBenhNhan": ma_benh_nhan,
        "maBacSi": ma_bac_si,
        "trieuChung": random.choice(symptoms),
        "chanDoan": random.choice(diagnoses),
        "ghiChuDonThuoc": fake.sentence(nb_words=6)
    }