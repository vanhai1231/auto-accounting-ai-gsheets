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
        "Bạn là trợ lý kế toán thông minh. Văn bản dưới đây là nội dung từ hóa đơn bán hàng, "
        "được tạo từ OCR nên có thể bị lỗi xuống dòng hoặc thiếu định dạng.\n\n"
        "Nhiệm vụ của bạn là trích xuất chính xác **các dòng hàng hóa** trong hóa đơn thành một mảng JSON chuẩn, "
        "mỗi phần tử là một dòng hàng gồm các trường:\n"
        "- \"ten_hang\": tên hàng hóa (ghép đủ nếu bị chia dòng),\n"
        "- \"ma_hang\": mã hàng (nếu có),\n"
        "- \"don_vi\": đơn vị tính (ví dụ: chiếc, bộ,...),\n"
        "- \"so_luong\": số lượng dạng số nguyên,\n"
        "- \"don_gia\": đơn giá (không có đơn vị tiền),\n"
        "- \"thanh_tien\": thành tiền (tính theo số lượng * đơn giá),\n"
        "- \"ngay\": ngày giao dịch (theo định dạng dd/mm/yyyy).\n\n"
        "Hãy suy luận và chuẩn hóa nếu thấy dữ liệu bị xuống dòng sai hoặc rối loạn thứ tự. "
        "Không trả lời gì ngoài đoạn JSON duy nhất. Không có bất kỳ mô tả, lời giải thích, dấu ``` hay văn bản phụ nào ngoài mảng JSON.\n\n"
        "Ví dụ:\n"
        "[\n"
        "  {\n"
        "    \"ten_hang\": \"Chuột không dây\",\n"
        "    \"ma_hang\": \"M001\",\n"
        "    \"don_vi\": \"Chiếc\",\n"
        "    \"so_luong\": 2,\n"
        "    \"don_gia\": 150000,\n"
        "    \"thanh_tien\": 300000,\n"
        "    \"ngay\": \"21/07/2025\"\n"
        "  },\n"
        "  ...\n"
        "]"
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
