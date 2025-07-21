import os, requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GROQ_API_KEY")
resp = requests.get("https://api.groq.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {key}"})
models = resp.json()
print("== Available Models ==")
for m in models.get("data", []):
    print("-", m.get("id"))
