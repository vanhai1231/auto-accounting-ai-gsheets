import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

# Khởi tạo client cho Groq API (OpenAI-style)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

DEFAULT_MODEL = "llama3-8b-8192"

def parse_invoice_with_groq(ocr_text: str,
                            model: str = DEFAULT_MODEL) -> list[dict] | None:
    """
    Gửi nội dung hóa đơn OCR tới LLM để trích xuất bảng dữ liệu dạng JSON.
    Kết quả trả về là list[dict] gồm các dòng hóa đơn.
    """

    system_prompt = (
        "Bạn là trợ lý kế toán. Hãy đọc nội dung hóa đơn sau và trích xuất danh sách dòng hàng "
        "thành mảng JSON theo mẫu:\n"
        "[\n"
        "  {\n"
        "    \"ten_hang\": \"Tên hàng hóa\",\n"
        "    \"ma_hang\": \"Mã hàng (nếu có)\",\n"
        "    \"don_vi\": \"Đơn vị\",\n"
        "    \"so_luong\": 1,\n"
        "    \"don_gia\": 2000000,\n"
        "    \"thanh_tien\": 2000000,\n"
        "    \"ngay\": \"20/07/2030\"\n"
        "  }, ...\n"
        "]\n"
        "Chỉ trả về đúng JSON, không giải thích thêm. Không có ký tự thừa trước hoặc sau JSON."
    )

    try:
        # Gọi LLM mà không ép kiểu output
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ocr_text}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        # Tự tìm đoạn JSON trong nội dung trả về
        start = content.find("[")
        end = content.rfind("]") + 1
        json_text = content[start:end]

        # In đoạn JSON raw (debug)
        print("\n[🔍 JSON Extracted Raw]:\n", json_text)

        # Parse JSON
        return json.loads(json_text)

    except json.JSONDecodeError:
        print("[⚠] Không parse được JSON từ kết quả LLM.")
        return None

    except Exception as e:
        print(f"[❌] Lỗi khi gọi LLM hoặc xử lý kết quả: {e}")
        return None
