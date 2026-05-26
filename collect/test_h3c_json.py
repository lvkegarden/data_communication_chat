import subprocess
import json
import sys

result = subprocess.run(
    [sys.executable, 'collect/run_h3c_collect.py'],
    capture_output=True,
    text=True,
    timeout=180,
    cwd='d:\\project\\ai\\localrest'
)

print(f"退出码: {result.returncode}")
print(f"stdout长度: {len(result.stdout)}")
print(f"stderr长度: {len(result.stderr)}")

if result.stdout:
    try:
        data = json.loads(result.stdout)
        print(f"\nJSON解析成功!")
        print(f"success: {data.get('success')}")
        print(f"total_products: {data.get('total_products')}")
        print(f"产品列表长度: {len(data.get('products', []))}")
        
        if data.get('products'):
            print(f"\n前3个产品:")
            for p in data['products'][:3]:
                print(f"  - {p.get('product_code')} | {p.get('category')} | {p.get('source')}")
    except json.JSONDecodeError as e:
        print(f"\nJSON解析失败: {e}")
        print(f"stdout前500字符: {result.stdout[:500]}")
else:
    print("\nstdout为空！")
    if result.stderr:
        print(f"stderr: {result.stderr[:500]}")
