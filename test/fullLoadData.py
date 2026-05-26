import sys
import io
import re
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

session = requests.Session()
session.headers.update(headers)

print('=' * 80)
print('获取完整的 loadData 函数')
print('=' * 80)

js_url = 'https://www-file.ruijie.com.cn/chineseResources/UIA/v5.0/RJ-js/index-v2.2.js?20250604'
js_resp = session.get(js_url, timeout=30)
js_content = js_resp.text

# 查找 loadData 函数的完整实现
# 先找到函数起始位置
func_start_pattern = r'function loadData\(p, typeId, order, orderField\)'
match = re.search(func_start_pattern, js_content)

if match:
    start_idx = match.start()
    # 从函数开始位置往后找，匹配花括号
    # 找到第一个 {
    brace_start = js_content.find('{', match.end())
    if brace_start >= 0:
        depth = 1
        brace_end = brace_start + 1
        while brace_end < len(js_content) and depth > 0:
            if js_content[brace_end] == '{':
                depth += 1
            elif js_content[brace_end] == '}':
                depth -= 1
            brace_end += 1
        
        full_func = js_content[start_idx:brace_end]
        print('完整 loadData 函数:')
        print('=' * 80)
        print(full_func)
        print('=' * 80)
        
        # 分析函数中的关键信息
        print('\n--- 函数分析 ---')
        
        # 查找 URL 或 API
        url_patterns = [
            r'url\s*:\s*["\']([^"\']+)["\']',
            r'url\s*=\s*["\']([^"\']+)["\']',
            r'action\s*=\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in url_patterns:
            urls = re.findall(pattern, full_func)
            if urls:
                print(f'\nURL 模式匹配:')
                for u in urls:
                    print(f'  {u}')
        
        # 查找 AJAX 相关
        ajax_patterns = [
            r'\$\.ajax\s*\(\{',
            r'ajax\s*\(',
            r'fetch\s*\(',
        ]
        
        for pattern in ajax_patterns:
            if re.search(pattern, full_func):
                print(f'\n找到 AJAX/fetch 调用: {pattern}')
        
        # 查找参数处理
        param_patterns = [
            r'data\s*:\s*\{',
            r'data\s*:\s*"[^"]+"',
            r'params\s*:',
        ]
        
        for pattern in param_patterns:
            if re.search(pattern, full_func):
                print(f'\n找到数据提交: {pattern}')
        
        # 查找成功回调
        success_pattern = r'success\s*:\s*function\s*\([^)]*\)\s*\{'
        if re.search(success_pattern, full_func):
            print(f'\n找到 success 回调函数')

else:
    print('未找到函数')

# 也搜索 index-v2.8.js
print('\n' + '=' * 80)
print('检查 index-v2.8.js')
print('=' * 80)

js_url2 = 'https://www-file.ruijie.com.cn/chineseResources/UIA/news/header/RJ-js/index-v2.8.js?20260512'
js_resp2 = session.get(js_url2, timeout=30)
js_content2 = js_resp2.text

if 'loadData' in js_content2:
    print('在 index-v2.8.js 中也有 loadData')
    match2 = re.search(func_start_pattern, js_content2)
    if match2:
        start_idx2 = match2.start()
        brace_start2 = js_content2.find('{', match2.end())
        if brace_start2 >= 0:
            depth = 1
            brace_end2 = brace_start2 + 1
            while brace_end2 < len(js_content2) and depth > 0:
                if js_content2[brace_end2] == '{':
                    depth += 1
                elif js_content2[brace_end2] == '}':
                    depth -= 1
                brace_end2 += 1
            
            full_func2 = js_content2[start_idx2:brace_end2]
            if full_func2 != full_func:
                print('\n不同的实现:')
                print(full_func2)
else:
    print('index-v2.8.js 中没有 loadData')
