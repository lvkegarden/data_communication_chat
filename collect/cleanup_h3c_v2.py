import sqlite3
import json

db_path = 'data/localrest.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 清理华三数据（保留核心产品）
# 交换机：只保留S开头的主流系列（S6xxx, S5xxx, S12xxx等核心/汇聚/接入）
# 无线：只保留WA/WX开头的AP系列

cursor.execute("SELECT id, product_code, series, category FROM product_specs WHERE source = '华三'")
rows = cursor.fetchall()

delete_ids = []
valid_count = {'交换机': 0, '无线': 0}

for id_, code, series, category in rows:
    is_valid = True
    
    if category == '交换机':
        # 只保留主流交换机系列
        # 核心/汇聚：S12xxx, S10xxx, S9xxx, S6xxx
        # 接入：S5xxx, S4xxx, S3xxx, S2xxx, S1xxx
        if not (series.startswith('S') and len(series) >= 4 and len(series) <= 12):
            is_valid = False
        # 排除带下划线的
        if '_' in series:
            is_valid = False
        # 排除过长的系列名
        if '-' in series and len(series.split('-')[0]) > 10:
            is_valid = False
    elif category == '无线':
        # 只保留WA/WX开头的AP
        if not (series.startswith('WA') or series.startswith('WX')):
            is_valid = False
        if len(series) < 4 or len(series) > 15:
            is_valid = False
        if '_' in series:
            is_valid = False
    
    if not is_valid:
        delete_ids.append((id_, code, series, category))
    else:
        valid_count[category] = valid_count.get(category, 0) + 1

print(f"华三产品统计:")
print(f"  交换机有效: {valid_count.get('交换机', 0)}")
print(f"  无线有效: {valid_count.get('无线', 0)}")
print(f"  待删除: {len(delete_ids)}")

if delete_ids:
    print(f"\n将删除的产品示例 (前20个):")
    for id_, code, series, category in delete_ids[:20]:
        print(f"  [{category}] {code}")
    
    delete_ids_only = [d[0] for d in delete_ids]
    
    # 删除关联数据
    cursor.execute("DELETE FROM product_spec_attributes WHERE product_id IN ({})".format(
        ','.join('?' * len(delete_ids_only))), delete_ids_only)
    cursor.execute("DELETE FROM crawl_records WHERE product_code IN ({})".format(
        ','.join('?' * len(delete_ids_only))), [d[1] for d in delete_ids])
    cursor.execute("DELETE FROM product_specs WHERE id IN ({})".format(
        ','.join('?' * len(delete_ids_only))), delete_ids_only)
    
    conn.commit()
    print(f"\n已删除 {len(delete_ids)} 个华三产品")

# 最终统计
cursor.execute("""
    SELECT source, category, COUNT(*) as count
    FROM product_specs
    GROUP BY source, category
    ORDER BY source, category
""")

print(f"\n最终数据库统计:")
for row in cursor.fetchall():
    print(f"  {row[0]} - {row[1]}: {row[2]} 个")

cursor.execute("SELECT COUNT(*) FROM product_specs")
total = cursor.fetchone()[0]
print(f"\n总计: {total} 个产品")

conn.close()
