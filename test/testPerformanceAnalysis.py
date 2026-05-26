import requests
import json
import time
import sys
import statistics
from datetime import datetime

PYTHON_API_URL = "http://localhost:5001/api/chat"

class PerformanceAnalyzer:
    def __init__(self):
        self.results = []
    
    def print_header(self, title):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def print_section(self, title):
        print("\n" + "-" * 80)
        print(f"  {title}")
        print("-" * 80)
    
    def test_single_request(self, model_provider, test_message, description):
        """
        测试单个请求的性能
        """
        self.print_section(f"测试: {description} ({model_provider.upper()})")
        
        payload = {
            "session_id": f"perf_test_{model_provider}_{int(time.time())}",
            "message": test_message,
            "flag": "y",
            "model_provider": model_provider
        }
        
        print(f"\n请求参数:")
        print(f"  session_id: {payload['session_id']}")
        print(f"  message: {test_message[:50]}...")
        print(f"  model_provider: {model_provider}")
        
        try:
            start_time = time.time()
            resp = requests.post(PYTHON_API_URL, json=payload, timeout=120)
            total_time = time.time() - start_time
            
            print(f"\n请求结果:")
            print(f"  HTTP状态码: {resp.status_code}")
            print(f"  总耗时: {total_time:.2f}s")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"  success: {data.get('success')}")
                print(f"  model_name: {data.get('model_name')}")
                
                msg = data.get('message', '')
                if msg:
                    print(f"  回答长度: {len(msg)} chars")
                
                result = {
                    'model': model_provider,
                    'description': description,
                    'total_time': total_time,
                    'status': 'success',
                    'response_length': len(msg)
                }
            else:
                print(f"  响应内容: {resp.text[:200]}")
                result = {
                    'model': model_provider,
                    'description': description,
                    'total_time': total_time,
                    'status': 'error',
                    'error': resp.text[:200]
                }
            
            self.results.append(result)
            return result
            
        except requests.exceptions.Timeout:
            print(f"  ⚠️ 请求超时!")
            result = {
                'model': model_provider,
                'description': description,
                'total_time': 120,
                'status': 'timeout'
            }
            self.results.append(result)
            return result
        except Exception as e:
            print(f"  ❌ 请求异常: {e}")
            result = {
                'model': model_provider,
                'description': description,
                'total_time': 0,
                'status': 'error',
                'error': str(e)
            }
            self.results.append(result)
            return result
    
    def test_multiple_requests(self, model_provider, test_message, description, count=3):
        """
        测试多个请求，计算平均耗时
        """
        self.print_section(f"多次请求测试: {description} ({model_provider.upper()})")
        print(f"测试次数: {count}次")
        
        times = []
        for i in range(count):
            print(f"\n第 {i+1}/{count} 次请求...")
            result = self.test_single_request(model_provider, test_message, description)
            if result['status'] == 'success':
                times.append(result['total_time'])
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            if len(times) > 1:
                std_dev = statistics.stdev(times)
            else:
                std_dev = 0
            
            print(f"\n统计结果:")
            print(f"  成功请求数: {len(times)}/{count}")
            print(f"  平均耗时: {avg_time:.2f}s")
            print(f"  最快: {min_time:.2f}s")
            print(f"  最慢: {max_time:.2f}s")
            if len(times) > 1:
                print(f"  标准差: {std_dev:.2f}s")
        
        return times
    
    def analyze_bottlenecks(self):
        """
        分析可能的性能瓶颈
        """
        self.print_header("性能瓶颈分析")
        
        print("""
根据代码流程分析，可能的性能瓶颈：

1. LLM API 调用（主要瓶颈）
   - 大模型API调用本身较慢
   - 网络延迟
   - API限流

2. 意图识别（使用全局LLM）
   - 每次请求都要调用一次LLM进行意图识别
   - 对于简单问题，这是额外开销

3. Prompt 数据获取
   - 产品数据从数据库查询
   - 竞品分析需要多次数据库查询

4. 工作流执行
   - LangGraph工作流执行
   - 多节点串行执行

5. 模型初始化
   - 每次请求可能都要重新初始化LLM客户端
""")
        
        print("\n建议查看Python服务日志，重点关注：")
        print("  - 'Intent Classification' 耗时")
        print("  - 'get_current_llm' 耗时")
        print("  - 'LLM invoke' 耗时")
        print("  - 各个节点的执行时间")
    
    def generate_report(self):
        """
        生成性能报告
        """
        self.print_header("性能测试报告")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n测试结果汇总:")
        print("-" * 80)
        
        for result in self.results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"\n{status_icon} {result['description']} ({result['model'].upper()})")
            print(f"   耗时: {result['total_time']:.2f}s")
            print(f"   状态: {result['status']}")
            if result['status'] == 'success':
                print(f"   回答长度: {result.get('response_length', 0)} chars")
        
        print("\n" + "=" * 80)


def main():
    analyzer = PerformanceAnalyzer()
    
    analyzer.print_header("性能分析测试")
    
    print("""
测试目标: 分析 Qwen 和 DeepSeek 的接口性能

测试方案:
1. 简单问题测试
2. 复杂问题测试
3. 产品相关查询测试

注意: 请同时查看 Python 服务的日志输出，
      重点关注各个阶段的耗时统计
""")
    
    test_cases = [
        {
            'message': "用一句话介绍什么是Python？",
            'description': "简单问题测试"
        },
        {
            'message': "请详细解释什么是机器学习，包括它的主要分类和应用场景？",
            'description': "复杂问题测试"
        },
        {
            'message': "查询产品 S5735-L8P4S-A-V2",
            'description': "产品查询测试"
        }
    ]
    
    print("\n" + "=" * 80)
    print("  第一阶段: Qwen 性能测试")
    print("=" * 80)
    
    for tc in test_cases:
        analyzer.test_single_request('qwen', tc['message'], tc['description'])
        time.sleep(1)
    
    print("\n" + "=" * 80)
    print("  第二阶段: DeepSeek 性能测试")
    print("=" * 80)
    
    for tc in test_cases:
        analyzer.test_single_request('deepseek', tc['message'], tc['description'])
        time.sleep(1)
    
    analyzer.generate_report()
    analyzer.analyze_bottlenecks()
    
    print("\n" + "=" * 80)
    print("建议:")
    print("  1. 查看 Python 服务终端的详细日志")
    print("  2. 对比 Qwen 和 DeepSeek 的响应时间")
    print("  3. 观察日志中各个阶段的耗时")
    print("  4. 如果发现某个阶段特别慢，就是瓶颈所在")
    print("=" * 80)


if __name__ == "__main__":
    main()
