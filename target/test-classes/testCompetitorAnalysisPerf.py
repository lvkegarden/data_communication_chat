import requests
import json
import time
import sys

JAVA_API_URL = "http://localhost:8080/api/chat/chat"
PRODUCT_DATA_API = "http://localhost:8080/api/product-data"

print("=" * 70)
print("竞品分析性能分析测试")
print("=" * 70)

print("\n测试场景:")
print("  产品: S5755")
print("  意图: 竞品分析")
print("  模型: qwen")

results = []

def test_step(description, func):
    """测试单个步骤的性能"""
    print(f"\n--- {description} ---")
    start = time.time()
    try:
        result = func()
        elapsed = time.time() - start
        print(f"  耗时: {elapsed:.2f}s ({elapsed*1000:.0f}ms)")
        results.append({
            "step": description,
            "elapsed": elapsed,
            "success": True
        })
        return result
    except Exception as e:
        elapsed = time.time() - start
        print(f"  耗时: {elapsed:.2f}s ({elapsed*1000:.0f}ms)")
        print(f"  错误: {e}")
        results.append({
            "step": description,
            "elapsed": elapsed,
            "success": False,
            "error": str(e)
        })
        return None

print("\n" + "=" * 70)
print("阶段1: 测试各个子组件的性能")
print("=" * 70)

# 测试1: 获取所有产品摘要
def test_get_all_products():
    resp = requests.get(f"{PRODUCT_DATA_API}/summary", timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        products = data.get("products", [])
        print(f"  获取产品数量: {len(products)}")
        return products
    return []

all_products = test_step("获取所有产品摘要", test_get_all_products)

# 测试2: 获取S5755产品详情
def test_get_s5755_detail():
    resp = requests.get(f"{PRODUCT_DATA_API}/detail/S5755-L8P4S-A-V2", timeout=30)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("success"):
            product = data.get("product", {})
            print(f"  产品名称: {product.get('product_name', 'N/A')}")
            print(f"  产品型号: {product.get('product_code', 'N/A')}")
            return product
    return None

s5755_detail = test_step("获取S5755产品详情", test_get_s5755_detail)

# 测试3: 获取几个候选竞品详情
def test_get_candidate_details():
    candidates = ["S5735-L8P4S-A-V2", "S5735-L24T4X-A", "S5731-S24T4X"]
    for code in candidates:
        try:
            resp = requests.get(f"{PRODUCT_DATA_API}/detail/{code}", timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    print(f"  ✓ {code}: 成功")
                else:
                    print(f"  ✗ {code}: 未找到")
            else:
                print(f"  ✗ {code}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"  ✗ {code}: 错误 - {e}")

test_step("获取候选竞品详情", test_get_candidate_details)

print("\n" + "=" * 70)
print("阶段2: 完整竞品分析请求测试")
print("=" * 70)

def test_full_competitor_analysis():
    payload = {
        "session_id": f"perf_test_competitor_{int(time.time())}",
        "message": "S5755竞品分析",
        "flag": "n",
        "model_provider": "qwen"
    }
    
    print(f"  请求参数:")
    print(f"    session_id: {payload['session_id']}")
    print(f"    message: {payload['message']}")
    
    resp = requests.post(JAVA_API_URL, json=payload, timeout=120)
    print(f"  HTTP状态码: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"  success: {data.get('success')}")
        print(f"  modelName: {data.get('modelName', 'N/A')}")
        print(f"  modelProvider: {data.get('modelProvider', 'N/A')}")
        
        if data.get("preview"):
            try:
                preview = json.loads(data["preview"])
                print(f"\n  预览信息:")
                print(f"    intent: {preview.get('intent', {}).get('intent', 'N/A')}")
                print(f"    api_request.model: {preview.get('api_request', {}).get('model', 'N/A')}")
                
                api_req = preview.get('api_request', {})
                messages = api_req.get('messages', [])
                if messages:
                    total_length = sum(len(m.get('content', '')) for m in messages)
                    print(f"    prompt总长度: {total_length} chars")
                    print(f"    message数量: {len(messages)}")
            except:
                print(f"  preview: {data['preview'][:200]}...")
        
        return data
    else:
        print(f"  错误: {resp.text[:500]}")
        return None

full_result = test_step("完整竞品分析请求（预览模式）", test_full_competitor_analysis)

print("\n" + "=" * 70)
print("阶段3: 性能瓶颈分析")
print("=" * 70)

print("\n耗时统计:")
total_time = 0
for r in results:
    icon = "✅" if r.get("success") else "❌"
    print(f"  {icon} {r['step']}: {r['elapsed']:.2f}s ({r['elapsed']*1000:.0f}ms)")
    if r.get("success"):
        total_time += r['elapsed']

print(f"\n  总计: {total_time:.2f}s")

print("\n" + "=" * 70)
print("瓶颈分析")
print("=" * 70)

print("""
竞品分析处理流程:

1. 意图识别 (LLM调用1)
   └─ 调用全局intent_router (qwen模型)
   └─ 预计耗时: 1-3秒

2. 数据获取阶段
   ├─ 获取所有产品摘要 (1次HTTP请求)
   ├─ 预筛选候选竞品 (本地处理)
   └─ 逐个获取竞品详情 (N次HTTP请求) ⚠️ 可能的瓶颈
        └─ 每个候选产品需要一次HTTP请求
        └─ 如果有10个候选，就是10次网络往返

3. 相似度评估 (本地处理)

4. LLM生成分析 (LLM调用2) ⚠️ 主要瓶颈
   └─ prompt可能很长（包含产品数据+竞品数据）
   └─ 大模型生成需要时间
   └─ 预计耗时: 5-15秒（取决于回答长度）

""")

print("请查看Python服务终端的详细日志，重点关注:")
print("  1. PERF: Intent Classification - 意图识别耗时")
print("  2. === Competitor Analysis Data Fetching ===")
print("     - Step 1: 获取所有产品摘要耗时")
print("     - Step 3: 逐个获取竞品详情的平均耗时")
print("     - Total Cost: 数据获取总耗时")
print("  3. PERF: Competitor Analysis LLM Call - LLM生成耗时")

print("\n" + "=" * 70)
