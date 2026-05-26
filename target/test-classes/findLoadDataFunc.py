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
print('深入分析 loadData 函数的实现')
print('=' * 80)

# 1. 先获取并解析内联 script 中的完整 loadData 函数
url = "https://www.ruijie.com.cn/cp/jh-all/"
resp = session.get(url, timeout=15)
resp.encoding = 'utf-8'
html = resp.text

# 提取所有内联 script
inline_scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html)

print(f'\n--- 搜索完整的 loadData 函数 ---')
for i, content in enumerate(inline_scripts):
    if 'function loadData' in content or 'loadData' in content:
        print(f'\n内联 script[{i}]:')
        
        # 尝试提取完整函数
        # 模式1: function loadData(pageNo, id) { ... }
        func_pattern = r'function\s+loadData\s*\([^)]*\)\s*\{[\s\S]*?^\s*\}'
        func_match = re.search(func_pattern, content, re.MULTILINE)
        
        if func_match:
            print('  找到完整 loadData 函数:')
            print(func_match.group(0))
        else:
            # 显示包含 loadData 的上下文
            lines = content.split('\n')
            for j, line in enumerate(lines):
                if 'loadData' in line.lower() or '$.ajax' in line or 'url:' in line or 'URL' in line:
                    # 显示前后 5 行
                    start = max(0, j - 10)
                    end = min(len(lines), j + 10)
                    for k in range(start, end):
                        marker = '-> ' if k == j else '   '
                        print(f'  {marker}{k}: {lines[k].strip()[:200]}')

print('\n' + '=' * 80)
print('分析 JavaScript 文件中的 loadData')
print('=' * 80)

# 2. 下载并分析关键 JavaScript 文件
js_files = [
    'https://www-file.ruijie.com.cn/chineseResources/UIA/v5.0/RJ-js/index-v2.2.js?20250604',
    'https://www-file.ruijie.com.cn/chineseResources/UIA/v5.0/header/js/header-load-v1.0.js?20260511',
    'https://www-file.ruijie.com.cn/chineseResources/UIA/news/js/common.js',
    'https://www-file.ruijie.com.cn/chineseResources/UIA/news/header/RJ-js/index-v2.8.js?20260512',
]

for js_url in js_files:
    try:
        js_resp = session.get(js_url, timeout=15)
        js_content = js_resp.text
        
        if 'loadData' in js_content:
            print(f'\n--- 在 {js_url} 中找到 loadData ---')
            
            # 查找函数定义
            func_patterns = [
                r'loadData\s*=\s*function\s*\([^)]*\)\s*\{',
                r'function\s+loadData\s*\([^)]*\)\s*\{',
                r'loadData\s*:\s*function\s*\([^)]*\)\s*\{',
            ]
            
            found = False
            for pattern in func_patterns:
                match = re.search(pattern, js_content)
                if match:
                    found = True
                    start_idx = match.start()
                    # 提取函数体（需要匹配花括号）
                    func_start = js_content.find('{', match.end())
                    if func_start >= 0:
                        # 简单的花括号匹配
                        depth = 1
                        func_end = func_start + 1
                        while func_end < len(js_content) and depth > 0:
                            if js_content[func_end] == '{':
                                depth += 1
                            elif js_content[func_end] == '}':
                                depth -= 1
                            func_end += 1
                        
                        func_code = js_content[start_idx:func_end]
                        print(f'函数代码:')
                        print(func_code)
                        break
            
            if not found:
                # 显示包含 loadData 的上下文
                lines = js_content.split('\n')
                for j, line in enumerate(lines):
                    if 'loadData' in line:
                        start = max(0, j - 5)
                        end = min(len(lines), j + 10)
                        for k in range(start, end):
                            marker = '-> ' if k == j else '   '
                            print(f'  {marker}{k}: {lines[k].strip()[:200]}')
                        
    except Exception as e:
        print(f'\n--- 下载 {js_url} 失败: {e} ---')
