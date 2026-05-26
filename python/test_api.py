import requests
import json

BASE_URL = "http://localhost:5001/api/intent"

def test_types():
    print("=== 1. 测试 /api/intent/types ===")
    r = requests.get(f"{BASE_URL}/types")
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Success: {data['success']}")
    print(f"Intent types count: {len(data['intent_types'])}")
    for t in data['intent_types']:
        print(f"  - {t['value']}: {t['description']}")
    print()

def test_analyze():
    print("=== 2. 测试 /api/intent/analyze ===")
    test_texts = [
        "你好，很高兴认识你",
        "帮我写一个Python的快速排序函数",
        "分析一下上个月的销售数据趋势",
        "如何制定一个有效的项目计划",
        "搜索最新的人工智能发展趋势",
        "帮我写一封商务邀请邮件",
        "什么是Transformer模型的工作原理",
        "今天天气怎么样",
        "再见，感谢帮助",
    ]
    
    for text in test_texts:
        r = requests.post(f"{BASE_URL}/analyze", json={"text": text})
        data = r.json()
        if data['success']:
            result = data['result']
            print(f"  '{text}'")
            print(f"    -> {result['intent']} (置信度: {result['confidence']:.2%})")
            print(f"    理由: {result['reason']}")
            if result['entities']:
                print(f"    实体: {result['entities']}")
            if result['subtasks']:
                print(f"    子任务数: {len(result['subtasks'])}")
            print()

def test_batch():
    print("=== 3. 测试 /api/intent/analyze/batch ===")
    texts = [
        "你好",
        "帮我写一个Python函数",
        "分析销售数据"
    ]
    r = requests.post(f"{BASE_URL}/analyze/batch", json={"texts": texts})
    data = r.json()
    print(f"Success: {data['success']}")
    print(f"Count: {data['count']}")
    for i, result in enumerate(data['results']):
        print(f"  [{i+1}] '{texts[i]}' -> {result['intent']}")
    print()

def test_history():
    print("=== 4. 测试 /api/intent/history ===")
    r = requests.get(f"{BASE_URL}/history")
    data = r.json()
    print(f"Success: {data['success']}")
    print(f"History count: {data['count']}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("意图识别 API 测试")
    print("=" * 60)
    print()
    
    try:
        test_types()
        test_analyze()
        test_batch()
        test_history()
        print("=" * 60)
        print("所有测试完成！")
        print("=" * 60)
    except Exception as e:
        print(f"测试失败: {e}")
