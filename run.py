import argparse
import os
from ocr.tesseract_ocr import extract_text_from_pdf_tesseract
from llm_parser.groq_invoice_parser import parse_invoice_with_groq
from sheets.write_to_sheets import write_to_google_sheet
from config import settings
from utils.logger import get_logger

logger = get_logger()

def process_invoice(pdf_path):
    try:
        print(f"\nĐang xử lý file: {pdf_path}")
        logger.info(f"Đang xử lý: {pdf_path}")

        # OCR
        text = extract_text_from_pdf_tesseract(pdf_path, lang="vie+eng")

        # LLM
        result = parse_invoice_with_groq(text)
        if isinstance(result, dict):
            items = result.get("items", [])
        else:
            items = result  # fallback nếu đã là list

        if not items:
            print("Không trích xuất được nội dung từ LLM.")
            logger.warning(f"Không trích xuất được nội dung từ: {pdf_path}")
            return

        print(f"Trích xuất {len(items)} dòng sản phẩm.")
        logger.info(f"Đã phân tích {len(items)} dòng từ Groq.")

        # Ghi vào Google Sheets
        write_to_google_sheet(
            settings.GOOGLE_SHEET_ID,
            settings.WORKSHEET_NAME,
            items
        )
        print("Đã ghi vào Google Sheets.")
        logger.info(f"Đã ghi vào Google Sheets: {pdf_path}")

    except Exception as e:
        print(f"Lỗi khi xử lý {pdf_path}: {e}")
        logger.error(f"Lỗi khi xử lý {pdf_path}: {e}")

def process_folder(folder_path):
    files = [f for f in os.listdir(folder_path) if f.lower().endswith((".pdf", ".jpg", ".png"))]
    if not files:
        print("Không tìm thấy file phù hợp trong thư mục.")
        return

    for filename in files:
        full_path = os.path.join(folder_path, filename)
        process_invoice(full_path)

def main():
    parser = argparse.ArgumentParser(description="Auto Accounting AI - Xử lý hóa đơn bằng AI & Google Sheets")
    parser.add_argument("--file", type=str, help="Đường dẫn tới file hóa đơn (PDF/JPG/PNG)")
    parser.add_argument("--folder", type=str, help="Đường dẫn tới thư mục chứa nhiều hóa đơn")
    args = parser.parse_args()

    if args.file:
        process_invoice(args.file)
    elif args.folder:
        process_folder(args.folder)
    else:
        print("Vui lòng cung cấp --file hoặc --folder")

if __name__ == "__main__":
    main()
