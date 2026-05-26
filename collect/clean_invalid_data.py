import sqlite3
import json
import re

db_path = 'data/localrest.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 清理异常产品名（包含乱码的）
cursor.execute("SELECT id, product_code, product_name, series, category, source FROM product_specs WHERE source = '华为'")

rows = cursor.fetchall()
cleaned = 0

for row in rows:
    id_, code, name, series, category, source = row
    
    # 检测是否包含非ASCII和非中文的异常字符
    has_garbled = bool(re.search(r'[çÂÃ©èêëàáâäåòóôöõùúûüýÿ]', name or ''))
    has_garbled = has_garbled or bool(re.search(r'[çÂÃ©èêëàáâäåòóôöõùúûüýÿ]', series or ''))
    
    if has_garbled:
        # 清理乱码
        clean_series = re.sub(r'[çÂÃ©èêëàáâäåòóôöõùúûüýÿ]', '', series or '')
        clean_series = clean_series.strip()
        
        # 如果是系列结尾的乱码，替换为"系列"
        if not clean_series.endswith('系列') and len(clean_series) < len(series or ''):
            clean_series += '系列'
        
        clean_name = name.replace(series or '', clean_series) if series else name
        
        cursor.execute("""
            UPDATE product_specs 
            SET product_name = ?, series = ?, product_code = ?
            WHERE id = ?
        """, (clean_name, clean_series, clean_series.replace(' ', '-'), id_))
        
        cleaned += 1
        print(f"清理: {series} -> {clean_series}")

# 删除异常产品（如 AirEngine-Wi）
cursor.execute("""
    DELETE FROM product_specs 
    WHERE series LIKE '%Wi%' AND series NOT LIKE '%Wifi%' AND series NOT LIKE '%Wi-Fi%'
""")
deleted_wi = cursor.rowcount
if deleted_wi > 0:
    print(f"删除了 {deleted_wi} 个异常产品 (AirEngine-Wi)")

# 删除规格字段少于5个的产品
cursor.execute("""
    DELETE FROM product_specs 
    WHERE source = '华为' AND (specs_json IS NULL OR json_extract(specs_json, '$.无线标准') IS NULL)
    AND category = '无线' AND series LIKE 'AirEngine%'
""")
deleted_invalid = cursor.rowcount
if deleted_invalid > 0:
    print(f"删除了 {deleted_invalid} 个缺少核心规格的无线产品")

conn.commit()

# 验证清理结果
cursor.execute("""
    SELECT COUNT(*) as total,
           SUM(CASE WHEN product_name LIKE '%ç%' OR product_name LIKE '%Â%' THEN 1 ELSE 0 END) as garbled_count,
           SUM(CASE WHEN specs_json IS NULL OR json_extract(specs_json, '$.无线标准') IS NULL THEN 1 ELSE 0 END) as missing_specs
    FROM product_specs 
    WHERE source = '华为' AND category = '无线'
""")

stats = cursor.fetchone()
print(f"\n清理后:")
print(f"  总数: {stats[0]}")
print(f"  乱码产品: {stats[1]}")
print(f"  缺少规格: {stats[2]}")

conn.close()
print(f"\n完成! 清理了 {cleaned} 个产品名")
