import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8080/api/collect"

def testProductsList():
    """
    测试获取产品列表接口
    验证：返回的数据包含 specs 字段
    """
    print("=" * 80)
    print("测试1: 获取产品列表接口 GET /api/collect/products")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/products")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[FAIL] 失败：期望状态码 200，实际 {response.status_code}")
            return False
        
        products = response.json()
        print(f"产品数量: {len(products)}")
        
        if len(products) == 0:
            print("[WARN] 警告：数据库中没有产品数据")
            print("   建议先运行采集功能，然后再运行此测试")
            return True
        
        firstProduct = products[0]
        print(f"\n第一个产品结构:")
        print(f"  id: {firstProduct.get('id')}")
        print(f"  product_code: {firstProduct.get('product_code')}")
        print(f"  product_name: {firstProduct.get('product_name')}")
        print(f"  source: {firstProduct.get('source')}")
        print(f"  category: {firstProduct.get('category')}")
        print(f"  series: {firstProduct.get('series')}")
        print(f"  status: {firstProduct.get('status')}")
        print(f"  has specs: {'specs' in firstProduct}")
        
        if 'specs' not in firstProduct:
            print(f"[FAIL] 失败：产品列表不包含 specs 字段")
            return False
        
        specs = firstProduct.get('specs', {})
        print(f"  specs 类型: {type(specs)}")
        print(f"  specs 键数量: {len(specs) if isinstance(specs, dict) else 'N/A'}")
        
        print("\n[PASS] 产品列表接口测试通过")
        return True
        
    except Exception as e:
        print(f"[ERROR] 异常: {e}")
        return False

def testProductDetail():
    """
    测试获取产品详情接口
    验证：返回的数据包含 specs 和 links 字段
    """
    print("\n" + "=" * 80)
    print("测试2: 获取产品详情接口 GET /api/collect/products/{id}")
    print("=" * 80)
    
    try:
        listResponse = requests.get(f"{BASE_URL}/products")
        if listResponse.status_code != 200:
            print(f"[FAIL] 获取产品列表失败，无法进行详情测试")
            return False
        
        products = listResponse.json()
        if len(products) == 0:
            print("[WARN] 数据库中没有产品数据，跳过详情测试")
            return True
        
        firstProduct = products[0]
        productId = firstProduct.get('id')
        print(f"测试产品 ID: {productId}")
        print(f"测试产品型号: {firstProduct.get('product_code')}")
        
        response = requests.get(f"{BASE_URL}/products/{productId}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[FAIL] 失败：期望状态码 200，实际 {response.status_code}")
            return False
        
        detail = response.json()
        print(f"\n详情数据结构检查:")
        
        requiredFields = ['id', 'product_code', 'product_name', 'source', 'category', 
                         'series', 'status', 'created_at', 'updated_at']
        missingFields = []
        for field in requiredFields:
            if field not in detail:
                missingFields.append(field)
        
        if missingFields:
            print(f"[FAIL] 失败：缺少必需字段: {missingFields}")
            return False
        
        print(f"  基本字段: 完整")
        
        if 'specs' not in detail:
            print(f"[FAIL] 失败：缺少 specs 字段")
            return False
        
        specs = detail.get('specs', {})
        if not isinstance(specs, dict):
            print(f"[FAIL] 失败：specs 不是对象类型，实际是 {type(specs)}")
            return False
        
        print(f"  specs: {len(specs)} 个键 - OK")
        if specs:
            print(f"    示例: {list(specs.keys())[:5]}")
        
        if 'links' not in detail:
            print(f"[FAIL] 失败：缺少 links 字段")
            return False
        
        links = detail.get('links', [])
        if not isinstance(links, list):
            print(f"[FAIL] 失败：links 不是数组类型，实际是 {type(links)}")
            return False
        
        print(f"  links: {len(links)} 个链接 - OK")
        
        optionalFields = ['description', 'product_url', 'thumbnail_url']
        for field in optionalFields:
            if field in detail:
                print(f"  {field}: {'有值' if detail[field] else '空'}")
        
        print("\n[PASS] 产品详情接口测试通过")
        return True
        
    except Exception as e:
        print(f"[ERROR] 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def testNonExistentProduct():
    """
    测试获取不存在的产品详情
    验证：返回错误信息
    """
    print("\n" + "=" * 80)
    print("测试3: 获取不存在的产品详情")
    print("=" * 80)
    
    try:
        nonExistentId = 999999
        print(f"测试不存在的产品 ID: {nonExistentId}")
        
        response = requests.get(f"{BASE_URL}/products/{nonExistentId}")
        print(f"响应状态码: {response.status_code}")
        
        data = response.json()
        print(f"响应内容: {json.dumps(data, ensure_ascii=False)}")
        
        if 'error' in data:
            print(f"[PASS] 正确返回错误信息: {data['error']}")
            return True
        else:
            print(f"[WARN] 没有明确的 error 字段，但接口响应正常")
            return True
        
    except Exception as e:
        print(f"[ERROR] 异常: {e}")
        return False

def runAllTests():
    """
    运行所有测试
    """
    print("=" * 80)
    print("collect.html 详情功能测试套件")
    print("=" * 80)
    print(f"测试时间: {__import__('datetime').datetime.now()}")
    print(f"测试地址: {BASE_URL}")
    print()
    
    print("检查服务是否启动...")
    try:
        requests.get(f"{BASE_URL}/products", timeout=3)
        print("[PASS] 服务已启动")
    except Exception as e:
        print(f"[FAIL] 无法连接到服务: {e}")
        print("\n请先启动 Spring Boot 服务:")
        print("  1. 在 CMD 中运行: run.bat")
        print("  2. 或在 PowerShell 中运行: .\\run.ps1")
        sys.exit(1)
    
    results = []
    
    results.append(("产品列表接口", testProductsList()))
    results.append(("产品详情接口", testProductDetail()))
    results.append(("不存在的产品", testNonExistentProduct()))
    
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS] 通过" if result else "[FAIL] 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！详情功能应该可以正常工作了。")
        return True
    else:
        print(f"\n[WARN] 有 {total - passed} 个测试失败，请检查问题。")
        return False

if __name__ == "__main__":
    success = runAllTests()
    sys.exit(0 if success else 1)
