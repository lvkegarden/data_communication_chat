import sqlite3

conn = sqlite3.connect('data/localrest.db')
cursor = conn.cursor()

cursor.execute("SELECT source, category, COUNT(*) as cnt FROM product_specs GROUP BY source, category ORDER BY source, category")
print('=' * 60)
print('数据库中产品统计')
print('=' * 60)
for row in cursor.fetchall():
    print(f'{row[0]} - {row[1]}: {row[2]} 个')

cursor.execute("SELECT COUNT(*) FROM product_specs WHERE source='锐捷' AND category='交换机'")
ruijie_switch_count = cursor.fetchone()[0]

print(f'\n锐捷官网显示: 166 款交换机')
print(f'实际采集到: {ruijie_switch_count} 个交换机')
print(f'采集覆盖率: {ruijie_switch_count/166*100:.1f}%')

cursor.execute("SELECT product_code FROM product_specs WHERE source='锐捷' AND category='交换机' ORDER BY product_code")
print(f'\n交换机型号列表 ({ruijie_switch_count} 个):')
for row in cursor.fetchall():
    print(f'  {row[0]}')

conn.close()
