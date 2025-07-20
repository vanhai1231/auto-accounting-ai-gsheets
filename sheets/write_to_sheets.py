import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDENTIALS_FILE = "config/gsheets_credentials.json"

def write_to_google_sheet(spreadsheet_id: str, worksheet_name: str, data: list[dict]):
    # Xác thực với Google bằng Service Account
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    # Mở Google Sheet và chọn worksheet
    sheet = client.open_by_key(spreadsheet_id)
    worksheet = sheet.worksheet(worksheet_name)

    # Ghi header nếu cần (chỉ làm một lần hoặc tùy check)
    headers = ["ten_hang", "ma_hang", "don_vi", "so_luong", "don_gia", "thanh_tien", "ngay"]
    worksheet.clear()
    worksheet.append_row(headers)

    # Ghi từng dòng dữ liệu
    for row in data:
        values = [row.get(h, "") for h in headers]
        worksheet.append_row(values)

    print("Đã ghi xong dữ liệu vào Google Sheets.")
