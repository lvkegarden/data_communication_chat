import sqlite3
import json
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'localrest.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, product_code, product_name, category, specs_json FROM product_specs WHERE category = '无线' LIMIT 10")

rows = cursor.fetchall()

print(f"共有 {len(rows)} 个无线产品样本\n")

for row in rows:
    id_, code, name, cat, specs_json = row
    print(f"产品: {code} - {name}")
    
    if specs_json:
        specs = json.loads(specs_json)
        print(f"  规格字段数: {len(specs)}")
        for key, val in list(specs.items())[:5]:
            print(f"  {key}: {val}")
    else:
        print("  [无规格数据]")
    
    print()

cursor.execute("""
    SELECT COUNT(*) as total,
           SUM(CASE WHEN specs_json IS NOT NULL AND specs_json != '{}' THEN 1 ELSE 0 END) as with_specs,
           SUM(CASE WHEN specs_json IS NULL OR specs_json = '{}' THEN 1 ELSE 0 END) as without_specs
    FROM product_specs 
    WHERE category = '无线'
""")

stats = cursor.fetchone()
print(f"\n无线产品规格统计:")
print(f"  总数: {stats[0]}")
print(f"  有规格: {stats[1]}")
print(f"  无规格: {stats[2]}")

cursor.execute("SELECT DISTINCT series FROM product_specs WHERE category = '无线' ORDER BY series")
series_list = cursor.fetchall()
print(f"\n所有无线产品系列:")
for s in series_list:
    print(f"  - {s[0]}")

conn.close()
