import sqlite3
import json

db_path = 'data/localrest.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 查看交换机产品的描述
cursor.execute("SELECT product_code, series, description FROM product_specs WHERE category = '交换机' ORDER BY product_code")
switch_rows = cursor.fetchall()

print(f"交换机产品 ({len(switch_rows)} 个):\n")

for row in switch_rows:
    desc = row['description'] or ''
    desc_preview = desc[:100] + '...' if len(desc) > 100 else desc
    has_desc = "[OK]" if len(desc) > 30 else "[无]"
    print(f"{has_desc} {row['product_code']} ({row['series']})")
    if has_desc == "[OK]":
        print(f"    描述: {desc_preview}")
    print()

# 查看无线AP产品的描述
cursor.execute("SELECT product_code, series, description FROM product_specs WHERE category = '无线' ORDER BY product_code")
wlan_rows = cursor.fetchall()

print(f"\n无线AP产品 ({len(wlan_rows)} 个):\n")

for row in wlan_rows:
    desc = row['description'] or ''
    desc_preview = desc[:100] + '...' if len(desc) > 100 else desc
    has_desc = "[OK]" if len(desc) > 30 else "[无]"
    print(f"{has_desc} {row['product_code']}")
    if has_desc == "[OK]":
        print(f"    描述: {desc_preview}")
    print()

print(f"\n统计:")
print(f"  交换机总数: {len(switch_rows)}")
print(f"  有描述交换机: {sum(1 for r in switch_rows if r['description'] and len(r['description']) > 30)}")
print(f"  无线总数: {len(wlan_rows)}")
print(f"  有描述无线: {sum(1 for r in wlan_rows if r['description'] and len(r['description']) > 30)}")

conn.close()
