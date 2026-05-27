import os
import sys
import unittest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))


class TestAdditionalConfigs(unittest.TestCase):
    
    def test_scraper_config_exists(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config',
            'scraper.yml'
        )
        self.assertTrue(os.path.exists(config_path),
                       f"爬虫配置文件不存在: {config_path}")
    
    def test_scraper_config_is_valid(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config',
            'scraper.yml'
        )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self.assertIn('scraper', config)
        
        scraper = config['scraper']
        self.assertIn('request_timeout', scraper)
        self.assertIn('request_delay', scraper)
        self.assertIn('max_retries', scraper)
        self.assertIn('user_agents', scraper)
        self.assertIn('headers', scraper)
        
        self.assertIsInstance(scraper['user_agents'], list)
        self.assertTrue(len(scraper['user_agents']) > 0)
        self.assertIsInstance(scraper['headers'], dict)
    
    def test_cors_config_exists(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config',
            'cors.yml'
        )
        self.assertTrue(os.path.exists(config_path),
                       f"CORS配置文件不存在: {config_path}")
    
    def test_cors_config_is_valid(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config',
            'cors.yml'
        )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self.assertIn('cors', config)
        
        cors = config['cors']
        self.assertIn('allowed_origins', cors)
        self.assertIn('allowed_methods', cors)
        self.assertIn('allowed_headers', cors)
        self.assertIn('max_age', cors)
        self.assertIn('allow_credentials', cors)
        
        self.assertIsInstance(cors['allowed_origins'], list)
        self.assertIsInstance(cors['allowed_methods'], list)
        
    def test_web_config_exists(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config',
            'web-config.js'
        )
        self.assertTrue(os.path.exists(config_path),
                       f"前端配置文件不存在: {config_path}")
    
    def test_all_config_files_have_comments(self):
        config_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config'
        )
        
        yml_files = [
            os.path.join(config_dir, 'llm.yml'),
            os.path.join(config_dir, 'prompts.yml'),
            os.path.join(config_dir, 'scraper.yml'),
            os.path.join(config_dir, 'cors.yml')
        ]
        
        for config_file in yml_files:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn('使用说明', content,
                         f"{os.path.basename(config_file)} 缺少使用说明注释")


if __name__ == '__main__':
    unittest.main(verbosity=2)
