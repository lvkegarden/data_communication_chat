import sqlite3
import json

db_path = 'data/localrest.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT product_code, product_name, series, specs_json 
    FROM product_specs 
    WHERE category = '无线' AND source = '华为'
    ORDER BY product_code
""")

rows = cursor.fetchall()

print(f"无线AP产品数量: {len(rows)}\n")

for row in rows:
    specs = json.loads(row['specs_json']) if row['specs_json'] else {}
    has_core = any(k in specs for k in ['交换容量', '最大速率', '包转发率'])
    
    status = "[OK]" if has_core else "[FAIL]"
    print(f"{status} {row['product_code']}")
    print(f"    系列: {row['series']}")
    if specs:
        print(f"    规格字段数: {len(specs)}")
        for k, v in list(specs.items())[:3]:
            print(f"    {k}: {v}")
    else:
        print("    [无规格]")
    print()

cursor.execute("""
    SELECT COUNT(*) as total,
           SUM(CASE WHEN specs_json IS NOT NULL AND json_extract(specs_json, '$."最大速率"') IS NOT NULL THEN 1 ELSE 0 END) as with_rate,
           SUM(CASE WHEN specs_json IS NOT NULL AND json_extract(specs_json, '$."交换容量"') IS NOT NULL THEN 1 ELSE 0 END) as with_capacity
    FROM product_specs 
    WHERE category = '无线' AND source = '华为'
""")

stats = cursor.fetchone()
print(f"\n统计:")
print(f"  总数: {stats['total']}")
print(f"  有速率规格: {stats['with_rate']}")
print(f"  有交换容量: {stats['with_capacity']}")

conn.close()
