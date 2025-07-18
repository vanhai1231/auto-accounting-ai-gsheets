from pdf2image import convert_from_path
import pytesseract
import os
import tempfile

def pdf_to_images(pdf_path):
    """Chuyển PDF sang danh sách ảnh từ các trang."""
    return convert_from_path(pdf_path, dpi=300)

def extract_text_from_pdf_tesseract(pdf_path, lang='vie+eng'):
    """OCR toàn bộ PDF bằng Tesseract."""
    images = pdf_to_images(pdf_path)
    all_text = []

    for idx, image in enumerate(images):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            image.save(tmp.name, format='PNG')
            text = pytesseract.image_to_string(tmp.name, lang=lang)
            all_text.append(f"--- Page {idx+1} ---\n{text}")

    return "\n\n".join(all_text)
