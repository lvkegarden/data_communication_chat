import requests
import json
import time
import sys

PYTHON_API_URL = "http://localhost:5001/api/chat"

print("=" * 60)
print("简单性能测试")
print("=" * 60)

test_cases = [
    {"model": "qwen", "msg": "用一句话介绍什么是Python？", "desc": "Qwen简单问题"},
    {"model": "deepseek", "msg": "用一句话介绍什么是Python？", "desc": "DeepSeek简单问题"},
    {"model": "qwen", "msg": "请详细解释什么是机器学习，包括它的主要分类和应用场景？", "desc": "Qwen复杂问题"},
    {"model": "deepseek", "msg": "请详细解释什么是机器学习，包括它的主要分类和应用场景？", "desc": "DeepSeek复杂问题"},
]

results = []

for tc in test_cases:
    print(f"\n--- {tc['desc']} ---")
    payload = {
        "session_id": f"simple_perf_{tc['model']}_{int(time.time())}",
        "message": tc["msg"],
        "flag": "y",
        "model_provider": tc["model"]
    }
    
    try:
        start = time.time()
        resp = requests.post(PYTHON_API_URL, json=payload, timeout=120)
        elapsed = time.time() - start
        
        print(f"HTTP状态: {resp.status_code}")
        print(f"总耗时: {elapsed:.2f}s")
        
        if resp.status_code == 200:
            data = resp.json()
            msg_len = len(data.get('message', ''))
            print(f"模型: {data.get('model_name', 'N/A')}")
            print(f"回答长度: {msg_len} chars")
            
            results.append({
                "desc": tc['desc'],
                "elapsed": elapsed,
                "msg_len": msg_len,
                "model": data.get('model_name', 'N/A'),
                "success": True
            })
        else:
            print(f"错误: {resp.text[:200]}")
            results.append({
                "desc": tc['desc'],
                "elapsed": elapsed,
                "success": False,
                "error": resp.text[:200]
            })
            
    except Exception as e:
        print(f"异常: {e}")
        results.append({
            "desc": tc['desc'],
            "success": False,
            "error": str(e)
        })

print("\n" + "=" * 60)
print("测试结果汇总")
print("=" * 60)

for r in results:
    if r["success"]:
        print(f"✅ {r['desc']}: {r['elapsed']:.2f}s ({r['msg_len']} chars)")
    else:
        print(f"❌ {r['desc']}: 失败 - {r.get('error', 'Unknown')}")

print("\n" + "=" * 60)
print("请查看Python服务终端的日志，重点关注：")
print("  - PERF: Intent Classification")
print("  - PERF: LLM Initialization")
print("  - PERF: General Chat LLM Call")
print("=" * 60)
