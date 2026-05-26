import requests
import json

BASE_URL = "http://localhost:8080/api/collect"

print("开始采集华三数据...")
response = requests.post(f"{BASE_URL}/h3c", timeout=180)
result = response.json()

print(f"\n采集结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
