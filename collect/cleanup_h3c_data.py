import sqlite3
import re

db_path = 'data/localrest.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 清理无效华三产品：
# 1. 删除包含下划线的产品名（应该是横杠）
# 2. 删除长度异常的产品名
# 3. 保留主流交换机/无线系列

cursor.execute("SELECT id, product_code, series FROM product_specs WHERE source = '华三'")
rows = cursor.fetchall()

delete_ids = []
valid_ids = []

for id_, code, series in rows:
    is_valid = True
    
    # 交换机系列应该是S开头，4-15个字符
    if series.startswith('S'):
        if len(series) < 4 or len(series) > 15:
            is_valid = False
        # 排除明显无效的模式
        if re.match(r'^S\d{1,2}$', series):  # S后面只有1-2位数字
            is_valid = False
    # 无线系列应该是WA/WX开头，5-15个字符  
    elif series.startswith('WA') or series.startswith('WX'):
        if len(series) < 5 or len(series) > 15:
            is_valid = False
    # AC系列
    elif series.startswith('AC'):
        if len(series) < 4 or len(series) > 15:
            is_valid = False
    # 其他系列（可能是错误数据）
    else:
        is_valid = False
    
    if is_valid:
        valid_ids.append(id_)
    else:
        delete_ids.append((id_, code, series))

print(f"华三产品统计:")
print(f"  总数: {len(rows)}")
print(f"  有效: {len(valid_ids)}")
print(f"  无效: {len(delete_ids)}")

if delete_ids:
    print(f"\n将删除的无效产品示例:")
    for id_, code, series in delete_ids[:15]:
        print(f"  {code} - {series}")
    
    # 删除无效产品及其关联属性
    delete_ids_only = [d[0] for d in delete_ids]
    
    cursor.execute("DELETE FROM product_spec_attributes WHERE product_id IN ({})".format(
        ','.join('?' * len(delete_ids_only))), delete_ids_only)
    deleted_attrs = cursor.rowcount
    print(f"\n删除了 {deleted_attrs} 条规格属性")
    
    cursor.execute("DELETE FROM crawl_records WHERE source = '华三' AND product_code IN ({})".format(
        ','.join('?' * len(delete_ids_only))), [d[1] for d in delete_ids])
    deleted_records = cursor.rowcount
    print(f"删除了 {deleted_records} 条爬取记录")
    
    cursor.execute("DELETE FROM product_specs WHERE id IN ({})".format(
        ','.join('?' * len(delete_ids_only))), delete_ids_only)
    deleted_products = cursor.rowcount
    print(f"删除了 {deleted_products} 个无效华三产品")

conn.commit()

# 最终统计
cursor.execute("""
    SELECT source, category, COUNT(*) as count
    FROM product_specs
    GROUP BY source, category
""")

print(f"\n清理后数据库统计:")
for row in cursor.fetchall():
    print(f"  {row[0]} - {row[1]}: {row[2]} 个")

cursor.execute("SELECT COUNT(*) FROM product_specs")
total = cursor.fetchone()[0]
print(f"\n总计: {total} 个产品")

conn.close()
