import sys
import io
import requests
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

urls = [
    "https://www.ruijie.com.cn/cp/jh-all/",
    "https://www.ruijie.com.cn/cp/wx-all/",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

session = requests.Session()
session.headers.update(headers)

for url in urls:
    print(f"\n{'='*60}")
    print(f"URL: {url}")
    print('='*60)
    
    try:
        response = session.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        if response.status_code == 200:
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.title.text if soup.title else 'No title'
            print(f"Title: {title}")
            
            print(f"\n--- All links starting with /cp/ ---")
            links = soup.find_all('a', href=True)
            cp_links = []
            for a in links:
                href = a['href']
                if href.startswith('/cp/'):
                    text = a.get_text(strip=True)
                    cp_links.append((text[:80], href))
            
            print(f"Found {len(cp_links)} /cp/ links:")
            for i, (text, href) in enumerate(cp_links[:50], 1):
                print(f"  [{i:02d}] {text[:50]:50} -> {href}")
            
            print(f"\n--- Product card elements ---")
            card_selectors = ['.product-card', '.product-item', '.product-list li', 
                            '[class*="product"]', '[class*="card"]', '.item']
            for selector in card_selectors:
                cards = soup.select(selector)
                if cards and len(cards) > 0:
                    print(f"\nSelector '{selector}': {len(cards)} elements")
                    for card in cards[:3]:
                        card_text = card.get_text(strip=True)[:100]
                        card_links = card.find_all('a', href=True)
                        print(f"  Card text: {card_text}")
                        for cl in card_links[:2]:
                            print(f"    -> {cl.get_text(strip=True)[:30]} | {cl['href']}")
            
            print(f"\n--- H1/H2/H3 headings ---")
            for h in soup.find_all(['h1', 'h2', 'h3']):
                text = h.get_text(strip=True)
                if text and len(text) > 3:
                    print(f"  {h.name}: {text[:80]}")
            
            print(f"\n--- Table content ---")
            tables = soup.find_all('table')
            print(f"Tables found: {len(tables)}")
            for i, table in enumerate(tables[:2]):
                print(f"\nTable {i+1}:")
                rows = table.find_all('tr')
                print(f"  Rows: {len(rows)}")
                for row in rows[:5]:
                    cells = row.find_all(['td', 'th'])
                    row_text = ' | '.join([c.get_text(strip=True)[:30] for c in cells])
                    print(f"    {row_text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
