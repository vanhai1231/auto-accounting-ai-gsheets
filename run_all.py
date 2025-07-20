from ocr.tesseract_ocr import extract_text_from_pdf_tesseract
from llm_parser.groq_invoice_parser import parse_invoice_with_groq
from sheets.write_to_sheets import write_to_google_sheet

PDF_PATH = "samples/invoice1.pdf"
SPREADSHEET_ID = "1zEeuoNSt0jzgSNrKdI6DJeqJVzlTc8NINRlBpOj99Uc"
WORKSHEET_NAME = "Trang tính1"

def main():
    print("Đang OCR hóa đơn...")
    ocr_text = extract_text_from_pdf_tesseract(PDF_PATH, lang="vie+eng")

    print("Gọi Groq để phân tích...")
    items = parse_invoice_with_groq(ocr_text)
    if not items:
        print("Không phân tích được nội dung.")
        return

    print("Ghi vào Google Sheets...")
    write_to_google_sheet(SPREADSHEET_ID, WORKSHEET_NAME, items)

    print("Đã hoàn tất!")

if __name__ == "__main__":
    main()
