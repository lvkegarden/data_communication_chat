import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from huawei_scraper import HuaweiScraper

# 清除日志文件
log_file = 'scraper.log'
if os.path.exists(log_file):
    os.remove(log_file)

scraper = HuaweiScraper()

# 只采集交换机
products = scraper.scrape_category("交换机", scraper.switch_url)

print(f"\n\n===== 最终结果 =====")
print(f"采集了 {len(products)} 个交换机产品")

for p in products:
    print(f"\n{p.product_code}:")
    print(f"  URL: {p.product_url}")
    print(f"  描述: {p.description[:80] if p.description else '无'}...")

# 检查日志
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"\n\n===== 日志文件内容 ({len(lines)} 行) =====")
    # 只显示 DEBUG 和 WARN 行
    debug_lines = [l.strip() for l in lines if '[DEBUG]' in l or '[WARN]' in l]
    for line in debug_lines[:30]:
        print(line)
    if len(debug_lines) > 30:
        print(f"... 还有 {len(debug_lines) - 30} 条 DEBUG/WARN 日志")
