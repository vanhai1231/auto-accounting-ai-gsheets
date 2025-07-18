from ocr.tesseract_ocr import extract_text_from_pdf_tesseract

text = extract_text_from_pdf_tesseract("samples/invoice1.pdf")
print(text)
