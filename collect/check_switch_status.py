import sqlite3
import json
import re

db_path = 'data/localrest.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT product_code, series, category, source, description, specs_json
    FROM product_specs 
    WHERE category = '交换机' AND source = '华为'
    ORDER BY product_code
""")

rows = cursor.fetchall()

print(f"交换机产品数量: {len(rows)}\n")

for row in rows:
    specs = json.loads(row['specs_json']) if row['specs_json'] else {}
    desc = row['description'] or ''
    desc_preview = desc[:80] if desc else '[无描述]'
    
    has_core = any(k in specs for k in ['交换容量', '包转发率', '产品定位'])
    status = "[OK]" if has_core else "[FAIL]"
    
    print(f"{status} {row['product_code']} ({row['series']})")
    print(f"    描述: {desc_preview}")
    if specs:
        print(f"    规格: {list(specs.keys())[:5]}")
    print()

conn.close()
