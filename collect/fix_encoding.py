import sqlite3
import re

db_path = 'data/localrest.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, product_code, product_name, series FROM product_specs WHERE source = '华为' AND category = '无线'")

rows = cursor.fetchall()
cleaned = 0

for row in rows:
    id_, code, name, series = row
    
    has_issue = False
    clean_series = series
    
    # 检测各种乱码模式
    if '³' in (series or ''):
        clean_series = series.replace('³系列', '系列').replace('³', '系列')
        has_issue = True
    
    if '系' in (series or '') and '列' not in (series or ''):
        has_issue = True
    
    if has_issue:
        clean_series = clean_series.strip()
        if not clean_series.endswith('系列'):
            clean_series = clean_series + '系列'
        
        clean_name = name.replace(series or '', clean_series) if series else name
        clean_code = clean_series.replace(' ', '-')
        
        cursor.execute("""
            UPDATE product_specs 
            SET product_name = ?, series = ?, product_code = ?
            WHERE id = ?
        """, (clean_name, clean_series, clean_code, id_))
        
        cleaned += 1
        print(f"修复: {series} -> {clean_series}")

conn.commit()
print(f"\n修复了 {cleaned} 个产品名")

# 最终验证
cursor.execute("SELECT series FROM product_specs WHERE source = '华为' AND category = '无线' ORDER BY series")
rows = cursor.fetchall()
print(f"\n最终产品列表 ({len(rows)} 个):")
for row in rows:
    print(f"  - {row[0]}")

conn.close()
