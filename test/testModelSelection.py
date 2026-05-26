import requests
import json
import time
import sys

PYTHON_API_URL = "http://localhost:5001/api/chat"
JAVA_API_URL = "http://localhost:8080/api/chat/chat"

def print_separator(title=None):
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)

def test_model_selection_python():
    """
    直接测试 Python 后端的模型选择功能
    """
    print_separator("测试: Python API 模型选择功能")
    
    test_message = "用一句话介绍什么是人工智能？（回答要简洁，不超过20字）"
    test_session_prefix = "test_model_"
    
    results = {
        'qwen': None,
        'deepseek': None
    }
    
    for model in ['qwen', 'deepseek']:
        print(f"\n[测试模型: {model.upper()}]")
        print("-" * 50)
        
        payload = {
            "session_id": f"{test_session_prefix}{model}_{int(time.time())}",
            "message": test_message,
            "flag": "y",
            "model_provider": model
        }
        
        print(f"请求参数:")
        print(f"  session_id: {payload['session_id']}")
        print(f"  message: {test_message}")
        print(f"  model_provider: {model}")
        
        try:
            start = time.time()
            resp = requests.post(PYTHON_API_URL, json=payload, timeout=60)
            elapsed = time.time() - start
            
            print(f"\n响应时间: {elapsed:.2f}s")
            print(f"HTTP状态码: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"\n响应数据:")
                print(f"  success: {data.get('success')}")
                print(f"  model_provider: {data.get('model_provider', 'N/A')}")
                print(f"  model_name: {data.get('model_name', 'N/A')}")
                
                if data.get('preview'):
                    try:
                        preview = json.loads(data['preview'])
                        print(f"\n预览报文:")
                        print(f"  model_provider: {preview.get('model_provider', 'N/A')}")
                        print(f"  model_name: {preview.get('model_name', 'N/A')}")
                        if preview.get('api_request'):
                            print(f"  api_request.model: {preview['api_request'].get('model', 'N/A')}")
                    except json.JSONDecodeError:
                        print(f"  preview: {data['preview'][:100]}...")
                
                if data.get('message'):
                    print(f"\n模型回答:")
                    print(f"  {data['message']}")
                
                results[model] = {
                    'success': data.get('success'),
                    'model_provider': data.get('model_provider'),
                    'model_name': data.get('model_name'),
                    'message': data.get('message', '')
                }
            else:
                print(f"请求失败: {resp.status_code}")
                print(f"响应内容: {resp.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            results[model] = {'error': str(e)}
    
    return results

def test_model_selection_java():
    """
    测试通过 Java 后端的模型选择功能
    """
    print_separator("测试: Java API 模型选择功能")
    
    test_message = "用一句话介绍什么是机器学习？（回答要简洁，不超过20字）"
    test_session_prefix = "test_java_model_"
    
    results = {
        'qwen': None,
        'deepseek': None
    }
    
    for model in ['qwen', 'deepseek']:
        print(f"\n[测试模型: {model.upper()}]")
        print("-" * 50)
        
        payload = {
            "session_id": f"{test_session_prefix}{model}_{int(time.time())}",
            "message": test_message,
            "flag": "y",
            "model_provider": model
        }
        
        print(f"请求参数:")
        print(f"  session_id: {payload['session_id']}")
        print(f"  message: {test_message}")
        print(f"  model_provider: {model}")
        
        try:
            start = time.time()
            resp = requests.post(JAVA_API_URL, json=payload, timeout=60)
            elapsed = time.time() - start
            
            print(f"\n响应时间: {elapsed:.2f}s")
            print(f"HTTP状态码: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"\n响应数据:")
                print(f"  success: {data.get('success')}")
                print(f"  modelProvider: {data.get('modelProvider', 'N/A')}")
                print(f"  modelName: {data.get('modelName', 'N/A')}")
                
                if data.get('preview'):
                    try:
                        preview = json.loads(data['preview'])
                        print(f"\n预览报文:")
                        print(f"  model_provider: {preview.get('model_provider', 'N/A')}")
                        print(f"  model_name: {preview.get('model_name', 'N/A')}")
                    except json.JSONDecodeError:
                        print(f"  preview: {data['preview'][:100]}...")
                
                if data.get('message'):
                    print(f"\n模型回答:")
                    print(f"  {data['message']}")
                
                results[model] = {
                    'success': data.get('success'),
                    'modelProvider': data.get('modelProvider'),
                    'modelName': data.get('modelName'),
                    'message': data.get('message', '')
                }
            else:
                print(f"请求失败: {resp.status_code}")
                print(f"响应内容: {resp.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            results[model] = {'error': str(e)}
    
    return results

def analyze_results(python_results, java_results):
    """
    分析测试结果，判断模型选择是否真正生效
    """
    print_separator("测试结果分析")
    
    print("\n[Python API 测试结果]")
    print("-" * 50)
    
    python_qwen = python_results.get('qwen', {})
    python_deepseek = python_results.get('deepseek', {})
    
    print(f"Qwen 测试:")
    print(f"  success: {python_qwen.get('success', 'N/A')}")
    print(f"  model_provider: {python_qwen.get('model_provider', 'N/A')}")
    print(f"  model_name: {python_qwen.get('model_name', 'N/A')}")
    if python_qwen.get('message'):
        print(f"  回答: {python_qwen['message']}")
    
    print(f"\nDeepSeek 测试:")
    print(f"  success: {python_deepseek.get('success', 'N/A')}")
    print(f"  model_provider: {python_deepseek.get('model_provider', 'N/A')}")
    print(f"  model_name: {python_deepseek.get('model_name', 'N/A')}")
    if python_deepseek.get('message'):
        print(f"  回答: {python_deepseek['message']}")
    
    print("\n[Java API 测试结果]")
    print("-" * 50)
    
    java_qwen = java_results.get('qwen', {})
    java_deepseek = java_results.get('deepseek', {})
    
    print(f"Qwen 测试:")
    print(f"  success: {java_qwen.get('success', 'N/A')}")
    print(f"  modelProvider: {java_qwen.get('modelProvider', 'N/A')}")
    print(f"  modelName: {java_qwen.get('modelName', 'N/A')}")
    if java_qwen.get('message'):
        print(f"  回答: {java_qwen['message']}")
    
    print(f"\nDeepSeek 测试:")
    print(f"  success: {java_deepseek.get('success', 'N/A')}")
    print(f"  modelProvider: {java_deepseek.get('modelProvider', 'N/A')}")
    print(f"  modelName: {java_deepseek.get('modelName', 'N/A')}")
    if java_deepseek.get('message'):
        print(f"  回答: {java_deepseek['message']}")
    
    print("\n[关键判断]")
    print("=" * 50)
    
    all_passed = True
    issues = []
    
    print("\n1. Python API 模型参数检查:")
    if python_qwen.get('model_provider') == 'qwen':
        print("   ✅ Qwen 请求返回 model_provider=qwen")
    else:
        print(f"   ❌ Qwen 请求返回 model_provider={python_qwen.get('model_provider')}")
        all_passed = False
        issues.append("Python API: Qwen model_provider 不正确")
    
    if python_deepseek.get('model_provider') == 'deepseek':
        print("   ✅ DeepSeek 请求返回 model_provider=deepseek")
    else:
        print(f"   ❌ DeepSeek 请求返回 model_provider={python_deepseek.get('model_provider')}")
        all_passed = False
        issues.append("Python API: DeepSeek model_provider 不正确")
    
    if python_qwen.get('model_name') and 'qwen' in python_qwen.get('model_name', '').lower():
        print("   ✅ Qwen 请求返回 model_name 包含 qwen")
    else:
        print(f"   ⚠️ Qwen 请求返回 model_name={python_qwen.get('model_name')}")
    
    if python_deepseek.get('model_name') and 'deepseek' in python_deepseek.get('model_name', '').lower():
        print("   ✅ DeepSeek 请求返回 model_name 包含 deepseek")
    else:
        print(f"   ⚠️ DeepSeek 请求返回 model_name={python_deepseek.get('model_name')}")
    
    print("\n2. Java API 模型参数检查:")
    if java_qwen.get('modelProvider') == 'qwen':
        print("   ✅ Qwen 请求返回 modelProvider=qwen")
    else:
        print(f"   ❌ Qwen 请求返回 modelProvider={java_qwen.get('modelProvider')}")
        all_passed = False
        issues.append("Java API: Qwen modelProvider 不正确")
    
    if java_deepseek.get('modelProvider') == 'deepseek':
        print("   ✅ DeepSeek 请求返回 modelProvider=deepseek")
    else:
        print(f"   ❌ DeepSeek 请求返回 modelProvider={java_deepseek.get('modelProvider')}")
        all_passed = False
        issues.append("Java API: DeepSeek modelProvider 不正确")
    
    print("\n3. 回答内容对比 (判断是否真的切换了模型):")
    qwen_msg = python_qwen.get('message', '')
    deepseek_msg = python_deepseek.get('message', '')
    
    if qwen_msg and deepseek_msg:
        if qwen_msg != deepseek_msg:
            print("   ✅ Qwen 和 DeepSeek 的回答不同")
            print(f"   Qwen: {qwen_msg[:50]}...")
            print(f"   DeepSeek: {deepseek_msg[:50]}...")
        else:
            print("   ⚠️ Qwen 和 DeepSeek 的回答完全相同")
            print("   这可能意味着:")
            print("   - 两个模型给出了相同的答案（对于简单问题可能）")
            print("   - 或者模型切换没有真正生效")
    else:
        print("   ⚠️ 无法对比回答内容（某些回答为空）")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ 所有参数检查通过！模型选择功能看起来正常。")
        print("   请检查 Python 服务的日志，确认实际调用的 API 端点。")
    else:
        print("❌ 发现问题：")
        for issue in issues:
            print(f"   - {issue}")
    print("=" * 70)
    
    return all_passed, issues

def main():
    print_separator("模型选择功能测试")
    print("测试目标: 验证选择 Qwen 和 DeepSeek 时是否真的调用了对应的 API")
    print("测试方式:")
    print("  1. 直接调用 Python API (端口 5001)")
    print("  2. 通过 Java API 调用 (端口 8080)")
    print("  3. 对比响应中的 model_provider 和 model_name")
    
    try:
        python_results = test_model_selection_python()
        java_results = test_model_selection_java()
        
        all_passed, issues = analyze_results(python_results, java_results)
        
        print("\n" + "=" * 70)
        print("建议:")
        print("  1. 查看 Python 服务终端的日志")
        print("  2. 日志中应该显示:")
        print("     - 'Model provider: qwen' 或 'Model provider: deepseek'")
        print("     - 'get_current_llm' 的详细信息")
        print("     - 'Actual LLM model' 和 'Actual LLM base_url'")
        print("  3. 如果 base_url 是:")
        print("     - https://dashscope.aliyuncs.com/... -> Qwen")
        print("     - https://api.deepseek.com/... -> DeepSeek")
        print("=" * 70)
        
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"\n测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
