from ocr.tesseract_ocr import extract_text_from_pdf_tesseract
from llm_parser.groq_invoice_parser import parse_invoice_with_groq
import json

def main():
    path = "samples/invoice1.pdf"

    print("Đang OCR hóa đơn...")
    ocr_text = extract_text_from_pdf_tesseract(path, lang="vie+eng")
    print("[OCR Text Extracted]:\n", ocr_text[:500], "\n...")

    print("\nĐang gọi Groq để phân tích dữ liệu...")
    result = parse_invoice_with_groq(ocr_text)

    if result is None:
        print("Không nhận được dữ liệu hợp lệ từ LLM.")
        return

    print("\n[Parsed Result - JSON]:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n[Dữ liệu từng dòng]:")
    for idx, row in enumerate(result, start=1):
        print(f"{idx}. {row['ten_hang']} | SL: {row['so_luong']} | ĐG: {row['don_gia']} | TT: {row['thanh_tien']}")

if __name__ == "__main__":
    main()
