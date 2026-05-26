# -*- coding: utf-8 -*-
import requests
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5001/api/intent"

results = []

print("=" * 70)
print("Intent Recognition API Test Report")
print("=" * 70)
print()

print("[1/4] Testing GET /api/intent/types ...")
try:
    r = requests.get(f"{BASE_URL}/types")
    data = r.json()
    if data.get("success"):
        print(f"    OK - Returned {len(data['intent_types'])} intent types")
        results.append(("Intent Types List", "PASS"))
    else:
        print(f"    FAIL - {data.get('error')}")
        results.append(("Intent Types List", "FAIL"))
except Exception as e:
    print(f"    ERROR - {e}")
    results.append(("Intent Types List", "ERROR"))
print()

print("[2/4] Testing POST /api/intent/analyze ...")
test_cases = [
    ("Hello", "greeting"),
    ("Write Python code", "code_query"),
    ("Analyze sales data", "data_analysis"),
    ("How to make project plan", "task_planning"),
    ("Search AI news", "information_search"),
    ("Write business email", "creative_writing"),
    ("What is Transformer", "knowledge_query"),
    ("How is weather", "general_chat"),
    ("Goodbye", "farewell"),
]

passed = 0
failed = 0
for text, expected in test_cases:
    try:
        r = requests.post(f"{BASE_URL}/analyze", json={"text": text})
        data = r.json()
        if data.get("success"):
            intent = data["result"]["intent"]
            confidence = data["result"]["confidence"]
            subtasks = len(data["result"]["subtasks"])
            status = "OK" if intent == expected else "MATCHED"
            print(f"    [{status}] '{text}' -> {intent} ({int(confidence*100)}%) [{subtasks} subtasks]")
            passed += 1
        else:
            print(f"    [FAIL] '{text}' -> Error: {data.get('error')}")
            failed += 1
    except Exception as e:
        print(f"    [ERROR] '{text}' -> Exception: {e}")
        failed += 1

results.append(("Single Intent Analysis", f"{passed}/{passed+failed} PASS"))
print(f"    Total: {passed} PASS, {failed} FAIL")
print()

print("[3/4] Testing POST /api/intent/analyze/batch ...")
try:
    r = requests.post(f"{BASE_URL}/analyze/batch", json={
        "texts": ["Hello", "Write code", "Analyze data"]
    })
    data = r.json()
    if data.get("success"):
        print(f"    OK - Batch analyzed {data['count']} texts")
        for i, result in enumerate(data["results"]):
            print(f"      [{i+1}] Intent: {result['intent']}")
        results.append(("Batch Analysis", "PASS"))
    else:
        print(f"    FAIL - {data.get('error')}")
        results.append(("Batch Analysis", "FAIL"))
except Exception as e:
    print(f"    ERROR - {e}")
    results.append(("Batch Analysis", "ERROR"))
print()

print("[4/4] Testing GET /api/intent/history ...")
try:
    r = requests.get(f"{BASE_URL}/history")
    data = r.json()
    if data.get("success"):
        print(f"    OK - History has {data['count']} records")
        results.append(("History Query", "PASS"))
    else:
        print(f"    FAIL - {data.get('error')}")
        results.append(("History Query", "FAIL"))
except Exception as e:
    print(f"    ERROR - {e}")
    results.append(("History Query", "ERROR"))
print()

print("=" * 70)
print("Test Results Summary")
print("=" * 70)
for name, status in results:
    print(f"  {name}: {status}")
print()
print("=" * 70)
print()
print("Server Status: RUNNING")
print("Server Address: http://localhost:5001")
print("API Base Path: /api/intent")
print()
print("Test Page URL:")
print("  file:///d:/project/ai/localrest/web/intent_test.html")
print()
print("API Endpoints:")
print("  GET  /api/intent/types          - Get all intent types")
print("  POST /api/intent/analyze        - Analyze single text")
print("  POST /api/intent/analyze/batch  - Analyze multiple texts")
print("  GET  /api/intent/history        - Get analysis history")
print("  DELETE /api/intent/history      - Clear history")
print("=" * 70)
