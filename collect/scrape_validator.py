import requests
from urllib.parse import urlparse, urljoin
from typing import Dict, Any


class ScrapeValidator:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.parsed_url = urlparse(target_url)
        self.base_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def check_robots_txt(self) -> Dict[str, Any]:
        robots_url = urljoin(self.base_url, '/robots.txt')
        result = {
            'available': False,
            'content': None,
            'allows_target': True,
            'disallowed_paths': [],
            'raw_content': None
        }
        
        try:
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                result['available'] = True
                result['raw_content'] = response.text
                
                target_path = self.parsed_url.path
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('disallow:'):
                        path = line.split(':', 1)[1].strip()
                        if path:
                            result['disallowed_paths'].append(path)
                            if path != '/' and target_path.startswith(path):
                                result['allows_target'] = False
        except Exception as e:
            result['error'] = str(e)
        
        return result

    def test_access(self) -> Dict[str, Any]:
        result = {
            'accessible': False,
            'status_code': None,
            'content_type': None,
            'content_length': 0,
            'title': None,
            'error': None
        }
        
        try:
            response = self.session.get(self.target_url, timeout=15, allow_redirects=True)
            result['status_code'] = response.status_code
            result['content_type'] = response.headers.get('Content-Type', '')
            result['content_length'] = len(response.content)
            
            if response.status_code == 200:
                result['accessible'] = True
                
                content_lower = response.text.lower()
                title_start = content_lower.find('<title>')
                title_end = content_lower.find('</title>')
                if title_start != -1 and title_end != -1:
                    original_start = response.text.lower().find('<title>') + 7
                    result['title'] = response.text[original_start:original_start + (title_end - title_start - 7)]
                
                result['has_content'] = result['content_length'] > 5000
            else:
                result['error'] = f"HTTP Status: {response.status_code}"
                
        except requests.exceptions.Timeout as e:
            result['error'] = f"Connection timeout: {e}"
        except requests.exceptions.ConnectionError as e:
            result['error'] = f"Connection error: {e}"
        except Exception as e:
            result['error'] = f"Error: {e}"
        
        return result

    def check_anti_scraping_indicators(self) -> Dict[str, Any]:
        result = {
            'has_captcha': False,
            'uses_cloudflare': False,
            'has_javascript_rendering': False,
            'headers_analysis': {}
        }
        
        try:
            response = self.session.get(self.target_url, timeout=15)
            headers = response.headers
            
            server = headers.get('Server', '').lower()
            result['headers_analysis']['server'] = server
            
            if 'cloudflare' in server or 'cf-ray' in headers:
                result['uses_cloudflare'] = True
            
            content = response.text.lower()
            
            captcha_keywords = ['captcha', 'recaptcha', 'hcaptcha', 'turnstile', '验证码']
            for keyword in captcha_keywords:
                if keyword in content:
                    result['has_captcha'] = True
                    break
            
            if 'application/json' in response.headers.get('Content-Type', ''):
                result['has_javascript_rendering'] = False
            else:
                script_count = content.count('<script')
                result['headers_analysis']['script_count'] = script_count
                if script_count > 10:
                    result['has_javascript_rendering'] = True
                    
        except Exception as e:
            result['error'] = str(e)
        
        return result

    def validate_all(self) -> Dict[str, Any]:
        print(f"=" * 60)
        print(f"开始验证网站爬取可行性: {self.target_url}")
        print(f"=" * 60)
        
        results = {
            'url': self.target_url,
            'base_url': self.base_url,
            'robots_txt': self.check_robots_txt(),
            'access_test': self.test_access(),
            'anti_scraping': self.check_anti_scraping_indicators()
        }
        
        print("\n--- 1. robots.txt 检查 ---")
        robots = results['robots_txt']
        if robots['available']:
            print("[OK] robots.txt 可访问")
            print(f"  允许爬取目标路径: {'是' if robots['allows_target'] else '否'}")
            if robots['disallowed_paths']:
                print(f"  禁止的路径: {robots['disallowed_paths'][:5]}")
            print(f"\nrobots.txt 内容预览:")
            if robots['raw_content']:
                print(robots['raw_content'][:2000])
        else:
            print("[FAIL] robots.txt 不可访问")
            if 'error' in robots:
                print(f"  错误: {robots['error']}")
        
        print("\n--- 2. 网站访问测试 ---")
        access = results['access_test']
        if access['accessible']:
            print("[OK] 网站可正常访问")
            print(f"  HTTP状态码: {access['status_code']}")
            print(f"  页面标题: {access['title'][:80] if access['title'] else '未找到'}")
            print(f"  内容大小: {access['content_length']} 字节")
        else:
            print("[FAIL] 网站访问失败")
            print(f"  HTTP状态码: {access['status_code']}")
            print(f"  错误: {access['error']}")
        
        print("\n--- 3. 反爬虫机制检测 ---")
        anti = results['anti_scraping']
        print(f"  Cloudflare保护: {'是' if anti['uses_cloudflare'] else '否'}")
        print(f"  验证码检测: {'是' if anti['has_captcha'] else '否'}")
        print(f"  可能需要JS渲染: {'是' if anti['has_javascript_rendering'] else '否'}")
        
        print("\n" + "=" * 60)
        print("评估结论:")
        print("=" * 60)
        
        can_scrape = True
        reasons = []
        
        if robots['available'] and not robots['allows_target']:
            can_scrape = False
            reasons.append("robots.txt 禁止爬取此路径")
        
        if not access['accessible']:
            can_scrape = False
            reasons.append("网站无法访问")
        
        if anti['uses_cloudflare']:
            reasons.append("检测到Cloudflare保护，可能需要特殊处理")
        
        if anti['has_captcha']:
            reasons.append("检测到验证码机制")
        
        if anti['has_javascript_rendering']:
            reasons.append("可能需要JavaScript渲染，建议使用Playwright/Selenium")
        
        if can_scrape:
            print("[OK] 网站可以进行基本的数据爬取")
        else:
            print("[FAIL] 网站爬取存在障碍")
        
        if reasons:
            print("\n注意事项:")
            for reason in reasons:
                print(f"  - {reason}")
        
        return results


def main():
    target_urls = [
        "https://e.huawei.com/cn/products/switches/",
        "https://e.huawei.com/cn/products/wlan/",
        "https://www.h3c.com/cn/Products_And_Solution/InterConnect/Products/Switches/",
        "https://www.h3c.com/cn/Products_And_Solution/InterConnect/Products/IP_Wlan/",
        "https://www.ruijie.com.cn/cp/jh-yqw/",
        "https://www.ruijie.com.cn/cp/wx/"
    ]
    
    all_results = []
    for url in target_urls:
        print(f"\n{'#' * 80}")
        print(f"验证: {url}")
        print(f"{'#' * 80}\n")
        try:
            validator = ScrapeValidator(url)
            results = validator.validate_all()
            all_results.append(results)
        except Exception as e:
            print(f"验证失败: {e}")
            all_results.append({'url': url, 'error': str(e)})
    
    print(f"\n\n{'=' * 80}")
    print("汇总结果")
    print(f"{'=' * 80}")
    for r in all_results:
        url = r.get('url', 'Unknown')
        name = url.split('/')[2] if '//' in url else url
        if 'error' in r:
            print(f"[FAIL] {name}: {r['error']}")
        else:
            access = r.get('access_test', {}).get('accessible', False)
            js_render = r.get('anti_scraping', {}).get('has_javascript_rendering', False)
            cloudflare = r.get('anti_scraping', {}).get('uses_cloudflare', False)
            status = "[OK]" if access else "[FAIL]"
            notes = []
            if js_render:
                notes.append("需JS渲染")
            if cloudflare:
                notes.append("有Cloudflare")
            note_str = f" ({', '.join(notes)})" if notes else ""
            print(f"{status} {name}{note_str}")
    
    return all_results


if __name__ == "__main__":
    main()
