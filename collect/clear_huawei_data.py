import sqlite3

db_path = 'data/localrest.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 删除华为产品的爬取记录
cursor.execute("DELETE FROM crawl_records WHERE source = '华为'")
deleted_records = cursor.rowcount
print(f"删除了 {deleted_records} 条爬取记录")

# 删除华为产品及其关联的规格属性
cursor.execute("SELECT id FROM product_specs WHERE source = '华为'")
product_ids = [row[0] for row in cursor.fetchall()]

if product_ids:
    cursor.execute("DELETE FROM product_spec_attributes WHERE product_id IN ({})".format(
        ','.join('?' * len(product_ids))), product_ids)
    deleted_attrs = cursor.rowcount
    print(f"删除了 {deleted_attrs} 条规格属性")

cursor.execute("DELETE FROM product_specs WHERE source = '华为'")
deleted_products = cursor.rowcount
print(f"删除了 {deleted_products} 个华为产品")

conn.commit()
print("清理完成！")

conn.close()
