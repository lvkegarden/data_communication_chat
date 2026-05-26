import requests
import json

url = "http://localhost:5001/api/chat"

payload = {
    "session_id": "simple_test",
    "message": "你好",
    "flag": "y"
}

print(f"发送请求: {json.dumps(payload, ensure_ascii=False)}")
response = requests.post(url, json=payload)
print(f"响应状态: {response.status_code}")
print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
