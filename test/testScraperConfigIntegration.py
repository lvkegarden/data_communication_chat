import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import config_loader as cl


class TestScraperConfigIntegration(unittest.TestCase):
    
    def setUp(self):
        cl._config_cache = {}
    
    def test_scraper_config_file_exists(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config',
            'scraper.yml'
        )
        self.assertTrue(os.path.exists(config_path),
                       f"爬虫配置文件不存在: {config_path}")
    
    def test_scraper_config_loader_functions(self):
        config = cl.get_scraper_config()
        self.assertIsInstance(config, dict)
        self.assertIn('scraper', config)
    
    def test_get_request_timeout(self):
        timeout = cl.get_request_timeout()
        self.assertIsInstance(timeout, int)
        self.assertGreater(timeout, 0)
    
    def test_get_request_delay(self):
        delay = cl.get_request_delay()
        self.assertIsInstance(delay, int)
        self.assertGreaterEqual(delay, 0)
    
    def test_get_max_retries(self):
        retries = cl.get_max_retries()
        self.assertIsInstance(retries, int)
        self.assertGreaterEqual(retries, 0)
    
    def test_get_random_user_agent(self):
        ua1 = cl.get_random_user_agent()
        ua2 = cl.get_random_user_agent()
        
        self.assertIsInstance(ua1, str)
        self.assertTrue(len(ua1) > 0)
        self.assertIsInstance(ua2, str)
        self.assertTrue(len(ua2) > 0)
    
    def test_get_scraper_headers(self):
        headers = cl.get_scraper_headers()
        
        self.assertIsInstance(headers, dict)
        self.assertIn('User-Agent', headers)
        self.assertIn('Accept', headers)
        self.assertIn('Accept-Language', headers)
    
    def test_base_scraper_imports_config_loader(self):
        scraper_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'collect',
            'base_scraper.py'
        )
        
        with open(scraper_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('config_loader', content,
                     "base_scraper.py 未导入 config_loader")
    
    def test_base_scraper_uses_config_headers(self):
        scraper_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'collect',
            'base_scraper.py'
        )
        
        with open(scraper_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('get_scraper_headers', content,
                     "base_scraper.py 未使用 get_scraper_headers")
    
    def test_removed_hardcoded_user_agent_in_base_scraper(self):
        scraper_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'collect',
            'base_scraper.py'
        )
        
        with open(scraper_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertNotIn("'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'", content,
                        "base_scraper.py 仍包含硬编码的 User-Agent")


if __name__ == '__main__':
    unittest.main(verbosity=2)
