import requests
import re
import json
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from base_scraper import BaseScraper, ProductInfo
from scraper_logger import log


# 华三交换机核心规格数据库
H3C_SWITCH_SPECS_DB = {
    'S9820': {
        '产品定位': '核心交换机',
        '适用场景': '大型企业、数据中心、园区网络',
        '交换容量': '25.6Tbps/槽位',
        '包转发率': '6240Mpps',
        '业务插槽数': '4-12个',
        '主控引擎': '2个（冗余）',
        '端口类型': 'GE/10GE/25GE/40GE/100GE',
        '电源': '交流/直流，1+1冗余',
        '最大功耗': '约5500W',
        '尺寸': '442mm×520mm×300mm（8U）',
        '重量': '约42kg',
        '工作温度': '0°C~45°C',
        '支持协议': 'MPLS/SRv6/VXLAN/EVPN',
    },
    'S9827': {
        '产品定位': '数据中心核心交换机',
        '适用场景': 'AIGC智算、高端数据中心',
        '交换容量': '51.2Tbps',
        '包转发率': '14400Mpps',
        '端口类型': '800GE/400GE/200GE/100GE',
        '电源': '交流/直流，1+1冗余',
        '最大功耗': '约6000W',
        '尺寸': '442mm×520mm×175mm（4U）',
        '重量': '约35kg',
        '工作温度': '0°C~45°C',
        '支持协议': 'RoCEv2/EVPN/VXLAN',
    },
    'S12500': {
        '产品定位': '核心交换机',
        '适用场景': '大型企业、数据中心',
        '交换容量': '20.48Tbps/槽位',
        '包转发率': '5760Mpps',
        '业务插槽数': '4-12个',
        '主控引擎': '2个（冗余）',
        '端口类型': 'GE/10GE/25GE/40GE/100GE',
        '电源': '交流/直流，1+1冗余',
        '最大功耗': '约5000W',
        '尺寸': '442mm×520mm×300mm（8U）',
        '重量': '约40kg',
        '工作温度': '0°C~45°C',
        '支持协议': 'MPLS/SRv6/VXLAN',
    },
    'S10500': {
        '产品定位': '核心交换机',
        '适用场景': '大型企业、园区网络',
        '交换容量': '14.4Tbps/槽位',
        '包转发率': '3840Mpps',
        '业务插槽数': '4-8个',
        '主控引擎': '2个（冗余）',
        '端口类型': 'GE/10GE/25GE/40GE/100GE',
        '电源': '交流/直流，1+1冗余',
        '最大功耗': '约4000W',
        '尺寸': '442mm×480mm×260mm（6U）',
        '重量': '约35kg',
        '工作温度': '0°C~45°C',
        '支持协议': 'MPLS/SRv6/VXLAN',
    },
    'S6860': {
        '产品定位': '汇聚交换机',
        '适用场景': '中型企业、园区汇聚',
        '交换容量': '3.2Tbps',
        '包转发率': '1200Mpps',
        '端口数量': '48个GE/10GE',
        '上行端口': '4个100GE QSFP28',
        '电源': '交流，1+1冗余',
        '最大功耗': '约300W',
        '尺寸': '442mm×380mm×43.6mm（1U）',
        '重量': '约7kg',
        '工作温度': '0°C~45°C',
        'PoE': '不支持',
    },
    'S6520X': {
        '产品定位': '汇聚/接入交换机',
        '适用场景': '中型企业、园区',
        '交换容量': '1.28Tbps/2.56Tbps（堆叠）',
        '包转发率': '480Mpps/960Mpps（堆叠）',
        '端口数量': '24/48个GE',
        '上行端口': '4个10GE SFP+',
        '电源': '交流，单电源',
        '最大功耗': '约120W',
        '尺寸': '442mm×220mm×43.6mm（1U）',
        '重量': '约4.8kg',
        '工作温度': '0°C~45°C',
        'PoE': '支持（部分型号）',
    },
    'S5130S': {
        '产品定位': '接入交换机',
        '适用场景': '企业接入层、桌面接入',
        '交换容量': '336Gbps',
        '包转发率': '96Mpps',
        '端口数量': '24/48个GE',
        '上行端口': '4个万兆SFP+',
        '电源': '交流，单电源',
        '最大功耗': '约55W',
        '尺寸': '442mm×220mm×43.6mm（1U）',
        '重量': '约4.5kg',
        '工作温度': '0°C~45°C',
        'PoE': '不支持',
    },
    'S5560S': {
        '产品定位': '接入交换机',
        '适用场景': '企业接入层、PoE场景',
        '交换容量': '336Gbps/1.68Tbps（堆叠）',
        '包转发率': '132Mpps/444Mpps（堆叠）',
        '端口数量': '24/48个GE',
        '上行端口': '4个万兆SFP+',
        '电源': '交流',
        '最大功耗': '约370W（PoE）',
        '尺寸': '442mm×220mm×43.6mm（1U）',
        '重量': '约4.6kg',
        '工作温度': '0°C~45°C',
        'PoE': '支持802.3af/at',
    },
}

# 华三无线AP核心规格数据库
H3C_WLAN_SPECS_DB = {
    'WA6520': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公、教室',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '1.775Gbps',
        '天线': '内置智能天线',
        '接入终端': '256个',
        '接口': '1个GE电口',
        'PoE': '支持802.3af/at',
        '尺寸': '180mm×180mm×35mm',
        '重量': '约0.45kg',
        '工作温度': '0°C~45°C',
    },
    'WA6620': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '企业办公、会议室',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '5.95Gbps',
        '天线': '内置智能天线',
        '接入终端': '512个',
        '接口': '1个GE电口 + 1个10GE SFP+',
        'PoE': '支持802.3at',
        '尺寸': '220mm×220mm×40mm',
        '重量': '约0.9kg',
        '工作温度': '0°C~45°C',
    },
    'WA7620': {
        '产品类型': '室内Wi-Fi 6 AP',
        '适用场景': '高密度场景、会议厅',
        '无线标准': 'Wi-Fi 6 (802.11ax)',
        '最大速率': '10.7Gbps',
        '天线': '内置智能天线',
        '接入终端': '1024个',
        '接口': '1个10GE电口',
        'PoE': '支持802.3at',
        '尺寸': '250mm×250mm×45mm',
        '重量': '约1.4kg',
        '工作温度': '0°C~45°C',
    },
    'WA5320': {
        '产品类型': '室内Wi-Fi 5 AP',
        '适用场景': '企业办公、教室',
        '无线标准': 'Wi-Fi 5 (802.11ac)',
        '最大速率': '1.267Gbps',
        '天线': '内置智能天线',
        '接入终端': '128个',
        '接口': '1个GE电口',
        'PoE': '支持802.3af/at',
        '尺寸': '180mm×180mm×35mm',
        '重量': '约0.4kg',
        '工作温度': '0°C~45°C',
    },
}


class H3CScraper(BaseScraper):
    
    def __init__(self):
        super().__init__(
            source="华三",
            base_url="https://www.h3c.com"
        )
        
        # 正确的华三产品页面URL
        self.switch_url = "https://www.h3c.com/cn/Products_And_Solution/InterConnect/Products/Switches/"
        self.wlan_url = "https://www.h3c.com/cn/Products_And_Solution/InterConnect/Products/IP_Wlan/"
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_category_urls(self) -> Dict[str, str]:
        return {
            "交换机": self.switch_url,
            "无线": self.wlan_url
        }
    
    def scrape_category(self, category: str, url: str) -> List[ProductInfo]:
        log(f"[INFO] 开始爬取华三 {category}: {url}")
        
        products = []
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                log(f"[WARN] 访问失败: HTTP {response.status_code}")
                return products
            
            response.encoding = 'utf-8'
            
            if not response.text or len(response.text) < 500:
                log("[WARN] 响应内容过少")
                return products
            
            html = response.text
            log(f"[DEBUG] {category}页面内容长度: {len(html)} 字节")
            
            product_data = self._extract_product_data(html, category)
            log(f"[INFO] 找到 {len(product_data)} 个产品系列")
            
            self._fetch_product_details(product_data)
            
            valid_products = 0
            invalid_products = 0
            for series_name, series_info in product_data.items():
                product = self._create_product_from_series(
                    category, series_name, series_info
                )
                if product:
                    products.append(product)
                    valid_products += 1
                else:
                    invalid_products += 1
            
            if invalid_products > 0:
                log(f"[WARN] 过滤了 {invalid_products} 个无效产品")
            
        except Exception as e:
            log(f"[ERROR] 爬取华三 {category} 时出错: {e}")
            import traceback
            traceback.print_exc()
            log(traceback.format_exc())
        
        return products
    
    def _extract_product_data(self, html: str, category: str) -> Dict[str, Dict[str, Any]]:
        products = {}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        if category == "交换机":
            products = self._extract_switch_products(soup)
        elif category == "无线":
            products = self._extract_wlan_products(soup)
        
        return products
    
    def _extract_switch_products(self, soup: BeautifulSoup) -> Dict[str, Dict[str, Any]]:
        products = {}
        log(f"[DEBUG] 开始提取华三交换机产品系列")
        
        switch_series_patterns = [
            r'\bS\d{3,5}[A-Za-z0-9_-]*\b',
        ]
        
        html = str(soup)
        log(f"[DEBUG] 华三交换机HTML内容长度: {len(html)} 字节")
        
        old_series_prefixes = [
            'S1000', 'S1008', 'S1016', 'S1024', 'S1026', 'S1048', 'S1050T',
            'S1200', 'S1208', 'S1209', 'S1224', 'S1248',
            'S1300', 'S1324', 'S1348',
            'S1500', 'S1526', 'S1550',
            'S1600', 'S1650', 'S1750',
            'S1800', 'S1850',
            'S2000', 'S2008', 'S2100', 'S2108', 'S2126',
            'S2600',
            'S3100', 'S3110', 'S3200', 'S3210',
            'S3600',
            'S5000', 'S5008', 'S5016', 'S5024', 'S5048',
            'S5100', 'S5110', 'S5120',
        ]
        
        total_matches = 0
        for pattern in switch_series_patterns:
            matches = re.findall(pattern, html)
            log(f"[DEBUG] 华三交换机正则模式 '{pattern}' 匹配到 {len(matches)} 个结果")
            total_matches += len(matches)
            
            for match in matches:
                clean_name = match.strip().rstrip('-')
                
                if not clean_name.startswith('S'):
                    continue
                
                if len(clean_name) < 4 or len(clean_name) > 30:
                    continue
                
                if '_' in clean_name:
                    continue
                
                is_old_series = False
                for prefix in old_series_prefixes:
                    if clean_name.startswith(prefix):
                        is_old_series = True
                        break
                
                if is_old_series:
                    continue
                
                if clean_name not in products:
                    products[clean_name] = {
                        'name': clean_name,
                        'description': '',
                        'features': [],
                        'specs': {},
                        'links': [],
                        'url': '',
                        'detail_url': ''
                    }
                    log(f"[DEBUG] 添加华三交换机系列: {clean_name}")
        
        log(f"[DEBUG] 共提取到 {len(products)} 个华三交换机系列，正则总匹配数: {total_matches}")
        
        self._extract_detail_urls_from_list(soup, products)
        
        self._extract_links_from_soup(soup, products)
        
        self._extract_specs_from_db(products)
        
        return products
    
    def _extract_wlan_products(self, soup: BeautifulSoup) -> Dict[str, Dict[str, Any]]:
        products = {}
        log(f"[DEBUG] 开始提取华三无线产品系列")
        
        # 只匹配WA/WX开头的无线系列
        wireless_series_patterns = [
            r'\bWA\d{3,5}[A-Za-z0-9_-]*\b',
            r'\bWX\d{3,5}[A-Za-z0-9_-]*\b',
        ]
        
        html = str(soup)
        log(f"[DEBUG] 华三无线HTML内容长度: {len(html)} 字节")
        
        total_matches = 0
        for pattern in wireless_series_patterns:
            matches = re.findall(pattern, html)
            log(f"[DEBUG] 华三无线正则模式 '{pattern}' 匹配到 {len(matches)} 个结果")
            total_matches += len(matches)
            
            for match in matches:
                clean_name = match.strip().rstrip('-')
                
                # 只保留WA/WX开头的无线系列
                if not (clean_name.startswith('WA') or clean_name.startswith('WX')):
                    continue
                
                if len(clean_name) < 4 or len(clean_name) > 30:
                    continue
                
                # 过滤掉组合名
                if '_' in clean_name:
                    continue
                
                if clean_name not in products:
                    products[clean_name] = {
                        'name': clean_name,
                        'description': '',
                        'features': [],
                        'specs': {},
                        'links': [],
                        'url': '',
                        'detail_url': ''
                    }
                    log(f"[DEBUG] 添加华三无线系列: {clean_name}")
        
        log(f"[DEBUG] 共提取到 {len(products)} 个华三无线系列，正则总匹配数: {total_matches}")
        
        self._extract_detail_urls_from_list(soup, products)
        
        self._extract_links_from_soup(soup, products)
        
        self._extract_specs_from_db(products)
        
        return products
    
    def _extract_detail_urls_from_list(self, soup: BeautifulSoup, products: Dict[str, Dict[str, Any]]):
        base_url = "https://www.h3c.com"
        log(f"[DEBUG] 开始提取华三产品详情页URL，当前产品数: {len(products)}")
        
        url_count = 0
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            
            if not href.startswith('/cn/'):
                continue
            
            full_url = urljoin(base_url, href)
            
            for series_name in list(products.keys()):
                if series_name.lower() in text.lower() or series_name.lower() in href.lower():
                    if not products[series_name]['detail_url']:
                        products[series_name]['detail_url'] = full_url
                        products[series_name]['url'] = full_url
                        
                        products[series_name]['links'].insert(0, {
                            'title': f'H3C {series_name} 产品详情',
                            'url': full_url,
                            'type': '产品详情'
                        })
                        url_count += 1
                        log(f"[DEBUG] 为 {series_name} 提取详情页URL: {full_url}")
                        break
        
        no_url_products = [name for name, info in products.items() if not info.get('detail_url')]
        if no_url_products:
            log(f"[WARN] 以下 {len(no_url_products)} 个华三产品未提取到详情页URL: {no_url_products[:10]}...")
        
        log(f"[DEBUG] 共提取 {url_count} 个华三产品详情页URL")
    
    def _extract_links_from_soup(self, soup: BeautifulSoup, products: Dict[str, Dict[str, Any]]):
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if not href or href.startswith('#') or href.startswith('javascript'):
                continue
            
            if href.startswith('/'):
                href = urljoin(self.base_url, href)
            
            link_type = self._classify_link(text, href)
            
            for series_name in products:
                if series_name.lower() in text.lower() or series_name.lower() in href.lower():
                    if link_type:
                        link_info = {
                            'title': text[:100] if text else link_type,
                            'url': href[:500],
                            'type': link_type
                        }
                        if link_info not in products[series_name]['links']:
                            products[series_name]['links'].append(link_info)
    
    def _classify_link(self, text: str, href: str) -> str:
        text_lower = text.lower()
        href_lower = href.lower()
        
        if '彩页' in text or 'brochure' in href_lower:
            return '彩页'
        elif '手册' in text or 'manual' in href_lower or 'guide' in href_lower:
            return '手册'
        elif '规格' in text or 'spec' in href_lower:
            return '规格参数'
        elif '白皮书' in text or 'whitepaper' in href_lower:
            return '白皮书'
        elif '了解更多' in text or '详情' in text:
            return '产品详情'
        elif '.pdf' in href_lower:
            return 'PDF文档'
        
        return ''
    
    def _extract_specs_from_db(self, products: Dict[str, Dict[str, Any]]):
        log(f"[DEBUG] 开始匹配华三产品规格数据库")
        matched_count = 0
        unmatched_count = 0
        
        for series_name, product_info in products.items():
            specs = {}
            match_source = '未匹配'
            
            normalized_name = series_name.replace('-', '')
            
            # 尝试交换机规格库
            for db_key, db_specs in H3C_SWITCH_SPECS_DB.items():
                db_key_normalized = db_key.replace('-', '')
                if db_key_normalized in normalized_name or normalized_name in db_key_normalized:
                    specs.update(db_specs)
                    matched_count += 1
                    match_source = f'交换机库-{db_key}'
                    log(f"[DEBUG] {series_name} 匹配到交换机规格库: {db_key}")
                    break
            
            # 尝试无线AP规格库
            if not specs:
                for db_key, db_specs in H3C_WLAN_SPECS_DB.items():
                    db_key_normalized = db_key.replace('-', '')
                    if db_key_normalized in series_name:
                        specs.update(db_specs)
                        matched_count += 1
                        match_source = f'无线AP库-{db_key}'
                        log(f"[DEBUG] {series_name} 匹配到无线AP规格库: {db_key}")
                        break
            
            # fallback逻辑
            if not specs:
                if 'S9820' in series_name or 'S12500' in series_name:
                    specs['产品定位'] = '核心交换机'
                    specs['适用场景'] = '大型企业、数据中心'
                    matched_count += 1
                    match_source = 'fallback-S9820/S12500'
                elif 'S10500' in series_name:
                    specs['产品定位'] = '核心交换机'
                    specs['适用场景'] = '大型企业、园区'
                    matched_count += 1
                    match_source = 'fallback-S10500'
                elif 'S6860' in series_name or 'S6520' in series_name:
                    specs['产品定位'] = '汇聚交换机'
                    specs['适用场景'] = '中型企业、园区'
                    matched_count += 1
                    match_source = 'fallback-S6860/S6520'
                elif 'S5130' in series_name or 'S5560' in series_name:
                    specs['产品定位'] = '接入交换机'
                    specs['适用场景'] = '企业接入层'
                    matched_count += 1
                    match_source = 'fallback-S5130/S5560'
                
                if not specs:
                    if 'WA' in series_name:
                        specs['产品类型'] = '无线接入点 (AP)'
                        specs['适用场景'] = '企业无线覆盖'
                        matched_count += 1
                        match_source = 'fallback-WA'
                    else:
                        unmatched_count += 1
                        log(f"[WARN] {series_name} 未能匹配任何规格")
            
            specs['品牌'] = '华三'
            specs['系列'] = series_name
            
            if specs:
                product_info['specs'] = specs
        
        log(f"[DEBUG] 华三规格匹配结果: 匹配 {matched_count} | 未匹配 {unmatched_count} | 总计 {len(products)}")
    
    def _fetch_product_details(self, product_data: Dict[str, Dict[str, Any]]):
        import time
        log(f"[DEBUG] ========== 开始抓取华三产品详情页 ==========")
        log(f"[DEBUG] 需要抓取详情页的产品数: {len(product_data)}")
        
        fetched_count = 0
        failed_count = 0
        skipped_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        for idx, (series_name, product_info) in enumerate(product_data.items(), 1):
            detail_url = product_info.get('detail_url', '') or product_info.get('url', '')
            
            if not detail_url:
                log(f"[DEBUG] [{idx}/{len(product_data)}] {series_name} 未找到详情页URL")
                skipped_count += 1
                continue
            
            log(f"[DEBUG] [{idx}/{len(product_data)}] 正在抓取 {series_name} 详情页: {detail_url}")
            
            try:
                response = self.session.get(detail_url, timeout=10)
                response.encoding = 'utf-8'
                
                log(f"[DEBUG] {series_name} 详情页HTTP状态: {response.status_code}, 内容长度: {len(response.text)} 字节")
                
                if response.status_code != 200:
                    log(f"[WARN] {series_name} 详情页访问失败: HTTP {response.status_code}")
                    failed_count += 1
                    consecutive_failures += 1
                    
                    if consecutive_failures >= max_consecutive_failures:
                        log(f"[WARN] 连续 {consecutive_failures} 次失败，停止抓取详情页")
                        break
                    continue
                
                consecutive_failures = 0
                
                desc = self._extract_description_from_detail(series_name, response.text)
                
                if desc:
                    product_info['description'] = desc
                    fetched_count += 1
                    log(f"[OK] {series_name} 提取到描述 (长度={len(desc)}: {desc[:60]}...")
                else:
                    log(f"[WARN] {series_name} 详情页未提取到有效描述")
                    failed_count += 1
                
                time.sleep(0.2)
                
            except requests.exceptions.Timeout:
                log(f"[WARN] {series_name} 详情页请求超时")
                failed_count += 1
                consecutive_failures += 1
                
                if consecutive_failures >= max_consecutive_failures:
                    log(f"[WARN] 连续 {consecutive_failures} 次失败，停止抓取详情页")
                    break
            except requests.exceptions.ConnectionError as e:
                log(f"[WARN] {series_name} 详情页连接错误: {e}")
                failed_count += 1
                consecutive_failures += 1
                
                if consecutive_failures >= max_consecutive_failures:
                    log(f"[WARN] 连续 {consecutive_failures} 次失败，停止抓取详情页")
                    break
            except Exception as e:
                log(f"[ERROR] {series_name} 详情页抓取失败: {e}")
                failed_count += 1
                consecutive_failures += 1
                
                if consecutive_failures >= max_consecutive_failures:
                    log(f"[WARN] 连续 {consecutive_failures} 次失败，停止抓取详情页")
                    break
        
        log(f"[DEBUG] ========== 华三详情页抓取完成 ==========")
        log(f"[INFO] 成功: {fetched_count} | 失败: {failed_count} | 跳过: {skipped_count} | 总计: {len(product_data)}")
    
    def _extract_description_from_detail(self, series_name: str, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content = meta_desc.get('content', '')
            if content and len(content) > 20:
                log(f"[DEBUG] {series_name} 从meta description提取到描述 (长度={len(content)})")
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
                log(f"[DEBUG] {series_name} 尝试选择器 '{selector}'，找到 {len(elements)} 个元素")
                for elem in elements:
                    text = elem.get_text(strip=True)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text and len(text) > 30 and len(text) < 2000:
                        log(f"[DEBUG] {series_name} 从 '{selector}' 提取到描述 (长度={len(text)})")
                        return text
        
        h1 = soup.find('h1')
        if h1:
            h1_text = h1.get_text(strip=True)
            if h1_text and len(h1_text) > 5:
                next_elem = h1.find_next_sibling()
                if next_elem and next_elem.name == 'p':
                    p_text = next_elem.get_text(strip=True)
                    p_text = re.sub(r'\s+', ' ', p_text).strip()
                    if len(p_text) > 30:
                        desc = h1_text + '。' + p_text
                        log(f"[DEBUG] {series_name} 从h1+p提取到描述 (长度={len(desc)})")
                        return desc
                log(f"[DEBUG] {series_name} 尝试从h1提取: '{h1_text[:60]}'")
                return h1_text
        
        paragraphs = soup.find_all('p')
        log(f"[DEBUG] {series_name} 页面共有 {len(paragraphs)} 个p标签")
        for p in paragraphs:
            text = p.get_text(strip=True)
            text = re.sub(r'\s+', ' ', text).strip()
            if (text and len(text) > 30 and len(text) < 1000 and
                not re.search(r'Copyright|©|Cookie|隐私|声明|版权|All rights', text)):
                if any(kw in text for kw in ['交换机', '核心', '企业', '园区', '数据中心', '高性能', '无线', 'AP']):
                    log(f"[DEBUG] {series_name} 从p标签提取到描述 (长度={len(text)})")
                    return text
        
        log(f"[DEBUG] {series_name} 所有策略均未提取到有效描述")
        return ''
    
    def _create_product_from_series(
        self, 
        category: str, 
        series_name: str, 
        series_info: Dict[str, Any]
    ) -> ProductInfo:
        if not series_name or len(series_name) < 3:
            return None
        
        product_code = series_name.replace(' ', '-')
        product_name = f"华三 {series_name} 系列"
        
        specs = series_info.get('specs', {})
        specs['品牌'] = '华三'
        specs['产品类型'] = category
        specs['系列'] = series_name
        
        description = series_info.get('description', '')
        links = series_info.get('links', [])
        
        return self.create_product_info(
            product_code=product_code,
            product_name=product_name,
            product_url=series_info.get('url', ''),
            category=category,
            series=series_name,
            description=description,
            specs=specs,
            links=links
        )
    
    def scrape_switch_products(self) -> List[ProductInfo]:
        return self.scrape_category("交换机", self.switch_url)
    
    def scrape_wlan_products(self) -> List[ProductInfo]:
        return self.scrape_category("无线", self.wlan_url)


def main():
    scraper = H3CScraper()
    
    print("=" * 60)
    print("华三数据采集 - 测试模式")
    print("=" * 60)
    
    result = scraper.scrape_all()
    
    print(f"\n{'=' * 60}")
    print(f"采集完成:")
    print(f"{'=' * 60}")
    print(f"产品总数: {len(result.products)}")
    print(f"成功分类: {result.success_count}")
    print(f"失败分类: {result.failed_count}")
    
    for i, product in enumerate(result.products[:10]):
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
