import requests
import re
import json
import time
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from base_scraper import BaseScraper, ProductInfo
from scraper_logger import log


RUIJIE_SWITCH_SPECS_DB = {
    'RG-S7800C': {
        '产品定位': '核心交换机',
        '适用场景': '大型企业、园区网络',
        '交换容量': '25.6Tbps/槽位',
        '包转发率': '6240Mpps',
    },
    'RG-S7600': {
        '产品定位': '核心交换机',
        '适用场景': '大型企业、园区网络',
        '交换容量': '10.4Tbps/槽位',
        '包转发率': '3840Mpps',
    },
    'RG-S6510': {
        '产品定位': '核心交换机',
        '适用场景': '大型企业、数据中心',
        '交换容量': '25.6Tbps/槽位',
        '包转发率': '6240Mpps',
    },
    'RG-S6220': {
        '产品定位': '汇聚交换机',
        '适用场景': '中型企业、园区汇聚',
        '交换容量': '3.2Tbps',
        '包转发率': '1200Mpps',
    },
    'RG-S5760': {
        '产品定位': '汇聚/接入交换机',
        '适用场景': '中型企业、园区',
        '交换容量': '1.28Tbps',
        '包转发率': '480Mpps',
    },
    'RG-S5310': {
        '产品定位': '接入交换机',
        '适用场景': '企业接入层',
        '交换容量': '336Gbps',
        '包转发率': '96Mpps',
    },
    'RG-S2910': {
        '产品定位': '接入交换机',
        '适用场景': '企业接入层',
        '交换容量': '336Gbps',
        '包转发率': '96Mpps',
    },
}

RUIJIE_WLAN_SPECS_DB = {
    'RG-AP820': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公、高密度场景',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '5.95Gbps',
    },
    'RG-AP720': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '1.775Gbps',
    },
    'RG-AP960': {
        '产品类型': '室内Wi-Fi 7 AP',
        '适用场景': '旗舰场景、超密集',
        '无线标准': 'Wi-Fi 7 (802.11be)',
        '最大速率': '10.7Gbps',
    },
    'RG-AP9861': {
        '产品类型': '室内Wi-Fi 7 AP',
        '适用场景': '旗舰场景、超密集',
        '无线标准': 'Wi-Fi 7 (802.11be)',
        '最大速率': '15.7Gbps',
    },
    'RG-AP9850': {
        '产品类型': '室内Wi-Fi 7 AP',
        '适用场景': '高密度场景',
        '无线标准': 'Wi-Fi 7 (802.11be)',
        '最大速率': '10.7Gbps',
    },
    'RG-AP9250': {
        '产品类型': '室内Wi-Fi 7 AP',
        '适用场景': '企业办公',
        '无线标准': 'Wi-Fi 7 (802.11be)',
        '最大速率': '5.95Gbps',
    },
    'RG-AP9220': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '1.775Gbps',
    },
    'RG-AP880': {
        '产品类型': '室外Wi-Fi 6 AP',
        '适用场景': '园区、室外覆盖',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '5.95Gbps',
    },
}


class RuijieScraper(BaseScraper):
    
    API_URL = 'https://www.ruijie.com.cn/application/api/product/getGoodsList'
    PAGE_SIZE = 12
    
    def __init__(self):
        super().__init__(
            source="锐捷",
            base_url="https://www.ruijie.com.cn"
        )
        
        self.switch_all_url = "https://www.ruijie.com.cn/cp/jh-all/"
        self.wlan_all_url = "https://www.ruijie.com.cn/cp/wx-all/"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
        })
    
    def get_category_urls(self) -> Dict[str, str]:
        return {
            "交换机": self.switch_all_url,
            "无线": self.wlan_all_url
        }
    
    def scrape_category(self, category: str, url: str) -> List[ProductInfo]:
        log(f"[INFO] 开始爬取锐捷 {category}（API 方式）")
        
        products = []
        
        try:
            log(f"[INFO] 正在从 {url} 获取分类 ID 和分页信息...")
            
            class_id = self._get_class_id_from_page(url)
            log(f"[INFO] 获取到分类 ID: {class_id}")
            
            if not class_id:
                log(f"[WARN] 未能获取到分类 ID，使用旧方式遍历子分类")
                return self._scrape_category_legacy(category, url)
            
            all_products = self._scrape_by_api(category, class_id, url)
            log(f"[INFO] API 方式共获取 {len(all_products)} 个产品")
            
            if all_products:
                self._fetch_product_details(all_products)
            
            valid_products = 0
            invalid_products = 0
            for model_name, model_info in all_products.items():
                product = self._create_product_from_model(
                    category, model_name, model_info
                )
                if product:
                    products.append(product)
                    valid_products += 1
                else:
                    invalid_products += 1
            
            if invalid_products > 0:
                log(f"[WARN] 过滤了 {invalid_products} 个锐捷无效产品")
            
            log(f"[INFO] 锐捷{category}最终采集 {valid_products} 个产品")
            
        except Exception as e:
            log(f"[ERROR] 爬取锐捷 {category} 时出错: {e}")
            import traceback
            log(traceback.format_exc())
        
        return products
    
    def _get_class_id_from_page(self, url: str) -> str:
        try:
            resp = self.session.get(url, timeout=30)
            if resp.status_code != 200:
                return ''
            
            resp.encoding = 'utf-8'
            html = resp.text
            
            pagination_pattern = r"loadData\('(\d+)','([^']+)'\)"
            matches = re.findall(pagination_pattern, html)
            if matches:
                class_ids = list(set(m[1] for m in matches))
                if class_ids:
                    return class_ids[0]
            
            soup = BeautifulSoup(html, 'html.parser')
            selected_tab = soup.find('a', class_='n-search-tab-selected')
            if selected_tab:
                class_id = selected_tab.get('id', '')
                if class_id:
                    return class_id
            
            all_tabs = soup.find_all('a', class_='n-search-tab')
            if all_tabs:
                for tab in all_tabs:
                    href = tab.get('href', '')
                    text = tab.get_text(strip=True)
                    if '全部' in text:
                        class_id = tab.get('id', '')
                        if class_id:
                            return class_id
            
            return ''
            
        except Exception as e:
            log(f"[ERROR] 获取 class_id 时出错: {e}")
            return ''
    
    def _scrape_by_api(self, category: str, class_id: str, referer_url: str) -> Dict[str, Dict[str, Any]]:
        products = {}
        base_url = "https://www.ruijie.com.cn"
        
        headers = self.session.headers.copy()
        headers['Referer'] = referer_url
        
        page = 1
        total_pages = 1
        total_products = 0
        all_items = []
        
        while page <= total_pages:
            log(f"[INFO] 正在请求第 {page}/{total_pages} 页...")
            
            params = {
                'page': page,
                'limit': self.PAGE_SIZE,
                'classId': class_id,
                'order': 2,
                'orderField': '',
                'screenValueIds': '',
            }
            
            try:
                resp = self.session.get(
                    self.API_URL,
                    params=params,
                    headers=headers,
                    timeout=30
                )
                
                if resp.status_code != 200:
                    log(f"[WARN] API 请求失败: HTTP {resp.status_code}")
                    break
                
                data = resp.json()
                
                if data.get('code') != 200:
                    log(f"[WARN] API 返回错误: {data.get('message')}")
                    break
                
                result_data = data.get('data', {})
                total = result_data.get('total', 0)
                items = result_data.get('list', [])
                
                if page == 1:
                    total_products = total
                    total_pages = (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE
                    log(f"[INFO] 总数: {total}, 总页数: {total_pages}")
                
                log(f"[INFO] 第 {page} 页获取到 {len(items)} 个商品")
                all_items.extend(items)
                
                page += 1
                time.sleep(0.3)
                
            except Exception as e:
                log(f"[ERROR] API 请求第 {page} 页时出错: {e}")
                break
        
        log(f"[INFO] API 共获取 {len(all_items)} 个商品（期望: {total_products}）")
        
        for idx, item in enumerate(all_items, 1):
            model_name = self._clean_model_name(item.get('modeName', ''))
            if not model_name:
                continue
            
            if category == "交换机":
                if not any(prefix in model_name for prefix in ['RG-S', 'RG-N', 'RG-IF', 'RG-SF', 'RG-MF', 'RG-MUX', 'RG-Lite', 'RG-IS', 'XS-S']):
                    continue
            elif category == "无线":
                if not any(prefix in model_name for prefix in ['RG-AP', 'RG-WS', 'RG-WIE', 'RG-MAP', 'RG-ANT', 'RG-IOA', 'RG-WIS', 'RG-AM', 'RG-APD']):
                    continue
            
            if len(model_name) < 5 or len(model_name) > 50:
                continue
            
            link_url = item.get('linkUrl') or item.get('rootlist', '')
            if link_url and not link_url.startswith('http'):
                link_url = urljoin(base_url, link_url)
            
            name = item.get('name', '')
            intro = item.get('introduction', '')
            remarks = item.get('remarks', '')
            remarks_array = item.get('remarksArray', [])
            
            description = intro or remarks or ''
            if not description and remarks_array:
                description = '；'.join(remarks_array)
            
            features = remarks_array if remarks_array else []
            
            if model_name not in products:
                products[model_name] = {
                    'name': model_name,
                    'description': description,
                    'features': features,
                    'specs': {},
                    'links': [],
                    'url': link_url,
                    'detail_url': link_url,
                    'subcategory': item.get('labelValueArray', []),
                    'api_item': item,
                }
                log(f"[DEBUG] 第{idx}个: 添加产品型号: {model_name}")
                if description:
                    log(f"        描述: {description[:60]}...")
                if link_url:
                    log(f"        详情页: {link_url}")
        
        self._extract_specs_from_db(products, category)
        
        return products
    
    def _scrape_category_legacy(self, category: str, url: str) -> List[ProductInfo]:
        log(f"[INFO] 使用旧方式（遍历子分类）爬取 {category}")
        
        switch_subcategories = [
            ("园区网交换机", "https://www.ruijie.com.cn/cp/jh-yqw/"),
            ("数据中心交换机", "https://www.ruijie.com.cn/cp/jh-shjzhx/"),
            ("行业精选交换机", "https://www.ruijie.com.cn/cp/jh-zxwljj/"),
            ("工业交换机", "https://www.ruijie.com.cn/cp/jh-gyjh/"),
        ]
        
        wlan_subcategories = [
            ("放装型无线AP", "https://www.ruijie.com.cn/cp/wx-fzhxwxjrd/"),
            ("墙面板型无线AP", "https://www.ruijie.com.cn/cp/wx-qmxap/"),
            ("智分型无线AP", "https://www.ruijie.com.cn/cp/wx-zfap/"),
            ("室外无线AP", "https://www.ruijie.com.cn/cp/wx-swap/"),
            ("无线控制器", "https://www.ruijie.com.cn/cp/wx-wxkzhq/"),
        ]
        
        products = []
        
        try:
            if category == "交换机":
                subcategories = switch_subcategories
            elif category == "无线":
                subcategories = wlan_subcategories
            else:
                subcategories = []
            
            log(f"[INFO] {category} 将遍历 {len(subcategories)} 个子分类")
            
            all_products = {}
            
            for idx, (subcat_name, subcat_url) in enumerate(subcategories, 1):
                log(f"[INFO] [{idx}/{len(subcategories)}] 正在爬取子分类: {subcat_name} -> {subcat_url}")
                
                subcat_products = self._scrape_subcategory(category, subcat_name, subcat_url)
                log(f"[INFO] 子分类 {subcat_name} 提取到 {len(subcat_products)} 个产品")
                
                for model_name, product_info in subcat_products.items():
                    if model_name not in all_products:
                        all_products[model_name] = product_info
                    else:
                        if product_info.get('description') and not all_products[model_name].get('description'):
                            all_products[model_name]['description'] = product_info.get('description')
                        if product_info.get('detail_url') and not all_products[model_name].get('detail_url'):
                            all_products[model_name]['detail_url'] = product_info.get('detail_url')
                            all_products[model_name]['url'] = product_info.get('url')
            
            log(f"[INFO] {category} 各子分类去重后共 {len(all_products)} 个产品")
            
            if all_products:
                self._fetch_product_details(all_products)
            
            valid_products = 0
            invalid_products = 0
            for model_name, model_info in all_products.items():
                product = self._create_product_from_model(
                    category, model_name, model_info
                )
                if product:
                    products.append(product)
                    valid_products += 1
                else:
                    invalid_products += 1
            
            if invalid_products > 0:
                log(f"[WARN] 过滤了 {invalid_products} 个锐捷无效产品")
            
            log(f"[INFO] 锐捷{category}最终采集 {valid_products} 个产品")
            
        except Exception as e:
            log(f"[ERROR] 爬取锐捷 {category} 时出错: {e}")
            import traceback
            log(traceback.format_exc())
        
        return products
    
    def _scrape_subcategory(self, category: str, subcat_name: str, url: str) -> Dict[str, Dict[str, Any]]:
        products = {}
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                log(f"[WARN] 访问 {subcat_name} 失败: HTTP {response.status_code}")
                return products
            
            response.encoding = 'utf-8'
            
            if not response.text or len(response.text) < 500:
                log(f"[WARN] {subcat_name} 响应内容过少")
                return products
            
            html = response.text
            log(f"[DEBUG] {subcat_name} 页面内容长度: {len(html)} 字节")
            
            soup = BeautifulSoup(html, 'html.parser')
            base_url = "https://www.ruijie.com.cn"
            
            product_cards = self._find_product_cards(soup)
            log(f"[DEBUG] {subcat_name} 找到 {len(product_cards)} 个产品卡片")
            
            for idx, card in enumerate(product_cards, 1):
                model, description, detail_url = self._parse_product_card(card, base_url)
                
                if not model:
                    continue
                
                if category == "交换机":
                    if not model.startswith('RG-S') and not model.startswith('RG-'):
                        continue
                    if not any(prefix in model for prefix in ['RG-S', 'RG-N', 'RG-IF', 'RG-SF', 'RG-MF', 'RG-MUX', 'RG-Lite']):
                        continue
                elif category == "无线":
                    if not any(prefix in model for prefix in ['RG-AP', 'RG-WS', 'RG-WIE', 'RG-MAP', 'RG-ANT']):
                        continue
                
                if len(model) < 5 or len(model) > 50:
                    continue
                
                if model not in products:
                    products[model] = {
                        'name': model,
                        'description': description or '',
                        'features': [],
                        'specs': {},
                        'links': [],
                        'url': detail_url or '',
                        'detail_url': detail_url or '',
                        'subcategory': subcat_name
                    }
                    log(f"[DEBUG] {subcat_name} 第{idx}个: 添加产品型号: {model}")
                    if description:
                        log(f"        描述: {description[:60]}...")
                    if detail_url:
                        log(f"        详情页: {detail_url}")
            
            self._extract_specs_from_db(products, category)
            
        except Exception as e:
            log(f"[ERROR] 爬取 {subcat_name} 时出错: {e}")
            import traceback
            log(traceback.format_exc())
        
        return products
    
    def _find_product_cards(self, soup: BeautifulSoup) -> List[Any]:
        cards = []
        
        all_divs = soup.find_all(['div', 'article', 'section'])
        for div in all_divs:
            classes = div.get('class', [])
            
            has_product_class = any(c for c in classes if 'product' in c.lower())
            has_card_class = any(c for c in classes if 'card' in c.lower())
            has_item_class = any(c for c in classes if 'item' in c.lower())
            
            if has_product_class or has_card_class or has_item_class:
                has_h2 = div.find('h2')
                has_link_with_rg = any(
                    link.get_text(strip=True).startswith('RG-') 
                    for link in div.find_all('a') 
                    if link.get_text(strip=True)
                )
                if has_h2 or has_link_with_rg:
                    cards.append(div)
        
        cards = list({id(c): c for c in cards}.values())
        
        return cards
    
    def _parse_product_card(self, card: BeautifulSoup, base_url: str) -> tuple:
        model = None
        description = None
        detail_url = None
        
        h2 = card.find('h2')
        if h2:
            model = h2.get_text(strip=True)
        
        h3 = card.find('h3')
        if h3:
            description = h3.get_text(strip=True)
        
        links = card.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.startswith('/cp/') and '.pdf' not in href.lower():
                detail_url = urljoin(base_url, href)
                break
        
        if not model:
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                if href.startswith('/cp/') and text and len(text) > 3:
                    if text.startswith('RG-'):
                        model = text
                        break
        
        if model:
            model = self._clean_model_name(model)
        
        return model, description, detail_url
    
    def _clean_model_name(self, model: str) -> str:
        model = model.strip()
        model = re.sub(r'\s+', '', model)
        model = model.replace('(V2)', '-V2')
        model = model.replace('(V3)', '-V3')
        model = model.replace('(V1)', '-V1')
        return model
    
    def _extract_specs_from_db(self, products: Dict[str, Dict[str, Any]], category: str):
        log(f"[DEBUG] 开始匹配锐捷产品规格数据库")
        matched_count = 0
        unmatched_count = 0
        
        for model_name, product_info in products.items():
            specs = {}
            
            normalized_name = model_name.replace('-', '').replace('RG-', '')
            
            specs_db = RUIJIE_SWITCH_SPECS_DB if category == "交换机" else RUIJIE_WLAN_SPECS_DB
            
            for db_key, db_specs in specs_db.items():
                db_key_normalized = db_key.replace('-', '').replace('RG-', '')
                if db_key_normalized in normalized_name:
                    specs.update(db_specs)
                    matched_count += 1
                    log(f"[DEBUG] {model_name} 匹配到规格库: {db_key}")
                    break
            
            if not specs:
                if category == "交换机":
                    if 'S78' in model_name or 'S76' in model_name:
                        specs['产品定位'] = '核心交换机'
                    elif 'S69' in model_name or 'S68' in model_name or 'S65' in model_name:
                        specs['产品定位'] = '核心/汇聚交换机'
                    elif 'S62' in model_name or 'S61' in model_name:
                        specs['产品定位'] = '汇聚交换机'
                    elif 'S57' in model_name or 'S53' in model_name:
                        specs['产品定位'] = '接入交换机'
                    elif 'S29' in model_name or 'S20' in model_name:
                        specs['产品定位'] = '接入交换机'
                    
                    if specs:
                        matched_count += 1
                    else:
                        unmatched_count += 1
                else:
                    if 'Wi-Fi 7' in product_info.get('description', ''):
                        specs['无线标准'] = 'Wi-Fi 7 (802.11be)'
                    elif 'Wi-Fi 6' in product_info.get('description', ''):
                        specs['无线标准'] = 'Wi-Fi 6 (802.11ax)'
                    specs['产品类型'] = '无线接入点 (AP)'
                    matched_count += 1
            
            specs['品牌'] = '锐捷'
            specs['产品类型'] = category
            specs['型号'] = model_name
            
            series = self._extract_series_from_model(model_name)
            if series:
                specs['系列'] = series
                product_info['series'] = series
            
            if specs:
                product_info['specs'] = specs
        
        log(f"[DEBUG] 锐捷规格匹配结果: 匹配 {matched_count} | 未匹配 {unmatched_count} | 总计 {len(products)}")
    
    def _extract_series_from_model(self, model: str) -> str:
        if model.startswith('RG-S'):
            match = re.match(r'RG-S(\d+)', model)
            if match:
                num = match.group(1)
                if num.startswith('7'):
                    return f"RG-S7000"
                elif num.startswith('6'):
                    return f"RG-S6000"
                elif num.startswith('5'):
                    return f"RG-S5000"
                elif num.startswith('3'):
                    return f"RG-S3000"
                elif num.startswith('2'):
                    return f"RG-S2000"
        elif model.startswith('RG-AP'):
            match = re.match(r'RG-AP(\d+)', model)
            if match:
                num = match.group(1)
                if num.startswith('9'):
                    return "RG-AP9000 (Wi-Fi 7)"
                elif num.startswith('8'):
                    return "RG-AP8000 (Wi-Fi 6)"
                elif num.startswith('7'):
                    return "RG-AP7000 (Wi-Fi 6)"
                elif num.startswith('6'):
                    return "RG-AP6000 (Wi-Fi 6)"
                elif num.startswith('1'):
                    return "RG-AP1000"
        
        return ""
    
    def _fetch_product_details(self, product_data: Dict[str, Dict[str, Any]]):
        import time
        log(f"[DEBUG] ========== 开始抓取锐捷产品详情页 ==========")
        log(f"[DEBUG] 需要抓取详情页的产品数: {len(product_data)}")
        
        fetched_count = 0
        failed_count = 0
        skipped_count = 0
        
        for idx, (model_name, product_info) in enumerate(product_data.items(), 1):
            detail_url = product_info.get('detail_url', '') or product_info.get('url', '')
            
            if not detail_url:
                log(f"[DEBUG] [{idx}/{len(product_data)}] {model_name} 未找到详情页URL")
                skipped_count += 1
                continue
            
            log(f"[DEBUG] [{idx}/{len(product_data)}] 正在抓取 {model_name} 详情页: {detail_url}")
            
            try:
                response = self.session.get(detail_url, timeout=20)
                response.encoding = 'utf-8'
                
                log(f"[DEBUG] {model_name} 详情页HTTP状态: {response.status_code}, 内容长度: {len(response.text)} 字节")
                
                if response.status_code != 200:
                    log(f"[WARN] {model_name} 详情页访问失败: HTTP {response.status_code}")
                    failed_count += 1
                    continue
                
                desc = self._extract_description_from_detail(model_name, response.text)
                
                if desc:
                    if not product_info.get('description'):
                        product_info['description'] = desc
                    fetched_count += 1
                    log(f"[OK] {model_name} 提取到描述 (长度={len(desc)}): {desc[:50]}...")
                else:
                    log(f"[DEBUG] {model_name} 详情页未提取到额外描述")
                
                specs_from_detail = self._extract_specs_from_detail(model_name, response.text)
                if specs_from_detail:
                    existing_specs = product_info.get('specs', {})
                    existing_specs.update(specs_from_detail)
                    product_info['specs'] = existing_specs
                    log(f"[OK] {model_name} 从详情页提取到 {len(specs_from_detail)} 个规格")
                
                time.sleep(0.2)
                
            except Exception as e:
                log(f"[ERROR] {model_name} 详情页抓取失败: {e}")
                failed_count += 1
        
        log(f"[DEBUG] ========== 锐捷详情页抓取完成 ==========")
        log(f"[INFO] 成功: {fetched_count} | 失败: {failed_count} | 跳过: {skipped_count} | 总计: {len(product_data)}")
    
    def _extract_description_from_detail(self, model_name: str, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content = meta_desc.get('content', '')
            if content and len(content) > 20:
                log(f"[DEBUG] {model_name} 从meta description提取到描述 (长度={len(content)})")
                return re.sub(r'\s+', ' ', content).strip()
        
        desc_selectors = [
            '.product-intro', '.product-description', '.intro-text',
            '.product-overview', '.overview-text',
            '.description', '.summary', '.product-brief',
            '[class*="overview"]', '[class*="intro"]', '[class*="description"]',
        ]
        
        for selector in desc_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text and len(text) > 30 and len(text) < 2000:
                        log(f"[DEBUG] {model_name} 从 '{selector}' 提取到描述 (长度={len(text)})")
                        return text
        
        return ''
    
    def _extract_specs_from_detail(self, model_name: str, html: str) -> Dict[str, str]:
        specs = {}
        soup = BeautifulSoup(html, 'html.parser')
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value and len(key) > 1 and len(key) < 30:
                        key = re.sub(r'\s+', '', key)
                        value = re.sub(r'\s+', ' ', value).strip()
                        if key not in specs and len(value) < 200:
                            specs[key] = value
        
        if specs:
            log(f"[DEBUG] {model_name} 从表格提取到 {len(specs)} 个规格")
        
        return specs
    
    def _create_product_from_model(
        self, 
        category: str, 
        model_name: str, 
        model_info: Dict[str, Any]
    ) -> ProductInfo:
        if not model_name or len(model_name) < 3:
            return None
        
        product_code = model_name.replace(' ', '-')
        product_name = f"锐捷 {model_name}"
        
        specs = model_info.get('specs', {})
        specs['品牌'] = '锐捷'
        specs['产品类型'] = category
        specs['型号'] = model_name
        
        series = model_info.get('series', '') or self._extract_series_from_model(model_name)
        
        description = model_info.get('description', '')
        links = model_info.get('links', [])
        
        if not links and model_info.get('detail_url'):
            links = [{
                'title': f'{model_name} 产品详情',
                'url': model_info['detail_url'],
                'type': '产品详情'
            }]
        
        return self.create_product_info(
            product_code=product_code,
            product_name=product_name,
            product_url=model_info.get('url', ''),
            category=category,
            series=series,
            description=description,
            specs=specs,
            links=links
        )
    
    def scrape_switch_products(self) -> List[ProductInfo]:
        return self.scrape_category("交换机", self.switch_all_url)
    
    def scrape_wlan_products(self) -> List[ProductInfo]:
        return self.scrape_category("无线", self.wlan_all_url)


def main():
    scraper = RuijieScraper()
    
    print("=" * 60)
    print("锐捷数据采集 - API 分页版")
    print("=" * 60)
    
    result = scraper.scrape_all()
    
    print(f"\n{'=' * 60}")
    print(f"采集完成:")
    print(f"{'=' * 60}")
    print(f"产品总数: {len(result.products)}")
    print(f"成功分类: {result.success_count}")
    print(f"失败分类: {result.failed_count}")
    
    switch_count = sum(1 for p in result.products if p.category == '交换机')
    wireless_count = sum(1 for p in result.products if p.category == '无线')
    print(f"交换机: {switch_count} 个")
    print(f"无线: {wireless_count} 个")
    
    for i, product in enumerate(result.products[:20]):
        print(f"\n  [{i+1}] {product.product_name}")
        print(f"      型号: {product.product_code}")
        print(f"      分类: {product.category}")
        print(f"      系列: {product.series}")
        if product.specs:
            print(f"      规格: {list(product.specs.keys())[:5]}")
        if product.description:
            print(f"      描述: {product.description[:50]}...")
    
    return result


if __name__ == "__main__":
    main()
