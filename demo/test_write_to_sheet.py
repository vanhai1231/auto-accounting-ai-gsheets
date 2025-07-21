from sheets.write_to_sheets import write_to_google_sheet

# ID của Google Sheet bạn cung cấp
SPREADSHEET_ID = "1zEeuoNSt0jzgSNrKdI6DJeqJVzlTc8NINRlBpOj99Uc"
WORKSHEET_NAME = "Trang tính1" 

# Dữ liệu test (giống kết quả parse invoice)
sample_data = [
    {
        "ten_hang": "Dịch vụ A",
        "ma_hang": "DV001",
        "don_vi": "gói",
        "so_luong": 2,
        "don_gia": 500000,
        "thanh_tien": 1000000,
        "ngay": "20/07/2030"
    },
    {
        "ten_hang": "Dịch vụ B",
        "ma_hang": "DV002",
        "don_vi": "giờ",
        "so_luong": 3,
        "don_gia": 300000,
        "thanh_tien": 900000,
        "ngay": "20/07/2030"
    }
]

write_to_google_sheet(SPREADSHEET_ID, WORKSHEET_NAME, sample_data)
