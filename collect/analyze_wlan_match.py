import sqlite3
import json
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'localrest.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, product_code, product_name, series, specs_json FROM product_specs WHERE category = '无线' ORDER BY series")

rows = cursor.fetchall()

print(f"无线AP产品规格详细分析:\n")

has_core_specs = []
no_core_specs = []

for row in rows:
    id_, code, name, series, specs_json = row
    
    specs = json.loads(specs_json) if specs_json else {}
    core_fields = ['最大速率', '无线标准', '接入终端']
    
    has_core = any(f in specs for f in core_fields)
    
    if has_core:
        has_core_specs.append({
            'series': series,
            'rate': specs.get('最大速率', '-'),
            'wifi': specs.get('无线标准', '-'),
            'terminals': specs.get('接入终端', '-'),
        })
    else:
        no_core_specs.append({
            'series': series,
            'spec_count': len(specs),
        })

print(f"成功匹配核心规格的产品 ({len(has_core_specs)} 个):")
for item in has_core_specs:
    print(f"  [OK] {item['series']}: {item['rate']} / {item['wifi']} / {item['terminals']}终端")

print(f"\n未匹配核心规格的产品 ({len(no_core_specs)} 个):")
for item in no_core_specs:
    print(f"  [FAIL] {item['series']}")

print(f"\n匹配成功率: {len(has_core_specs)}/{len(rows)} = {len(has_core_specs)*100//len(rows)}%")

conn.close()
