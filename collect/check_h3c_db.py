import sqlite3
import json

db_path = 'data/localrest.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT source, category, COUNT(*) as count
    FROM product_specs
    GROUP BY source, category
    ORDER BY source, category
""")

rows = cursor.fetchall()
print("数据库中的产品统计:\n")
for row in rows:
    print(f"  {row[0]} - {row[1]}: {row[2]} 个")

cursor.execute("SELECT COUNT(*) FROM product_specs")
total = cursor.fetchone()[0]
print(f"\n总计: {total} 个产品")

# 显示最近的华三产品
cursor.execute("""
    SELECT product_code, product_name, category, source, 
           CASE WHEN description IS NOT NULL AND LENGTH(description) > 10 THEN '有描述' ELSE '无描述' END as desc_status
    FROM product_specs 
    WHERE source = '华三'
    ORDER BY created_at DESC
    LIMIT 10
""")

rows = cursor.fetchall()
if rows:
    print(f"\n最近采集的华三产品:")
    for row in rows:
        print(f"  {row[0]} | {row[1][:40]} | {row[2]} | {row[4]}")
else:
    print("\n[WARN] 数据库中没有华三产品！")

conn.close()
