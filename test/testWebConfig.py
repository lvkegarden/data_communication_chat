import os
import sys
import unittest
import re


class TestWebConfig(unittest.TestCase):
    
    def setUp(self):
        self.config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config',
            'web-config.js'
        )
    
    def test_config_file_exists(self):
        self.assertTrue(
            os.path.exists(self.config_path),
            f"配置文件不存在: {self.config_path}"
        )
    
    def test_config_contains_required_structure(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('window.AppConfig', content,
                     "缺少 window.AppConfig 定义")
        self.assertIn('javaBaseUrl', content,
                     "缺少 javaBaseUrl 配置")
        self.assertIn('pythonBaseUrl', content,
                     "缺少 pythonBaseUrl 配置")
    
    def test_api_urls_are_valid(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        java_match = re.search(r"javaBaseUrl:\s*['\"]([^'\"]+)['\"]", content)
        python_match = re.search(r"pythonBaseUrl:\s*['\"]([^'\"]+)['\"]", content)
        
        self.assertIsNotNone(java_match, "javaBaseUrl 格式不正确")
        self.assertIsNotNone(python_match, "pythonBaseUrl 格式不正确")
        
        java_url = java_match.group(1)
        python_url = python_match.group(1)
        
        self.assertTrue(java_url.startswith('http'),
                       f"javaBaseUrl 应以 http 开头: {java_url}")
        self.assertTrue(python_url.startswith('http'),
                       f"pythonBaseUrl 应以 http 开头: {python_url}")
    
    def test_web_html_files_use_config_or_hardcoded(self):
        web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
        
        html_files = [
            os.path.join(web_dir, 'chat.html'),
            os.path.join(web_dir, 'product_agent.html'),
            os.path.join(web_dir, 'collect.html'),
            os.path.join(web_dir, 'index.html'),
            os.path.join(web_dir, 'intent_test.html')
        ]
        
        for html_file in html_files:
            if os.path.exists(html_file):
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_hardcoded = 'localhost:8080' in content or 'localhost:5001' in content
                has_config_import = 'web-config.js' in content or 'AppConfig' in content
                
                if has_hardcoded and not has_config_import:
                    print(f"[警告] {os.path.basename(html_file)} 仍使用硬编码的 API 地址")
    
    def test_android_web_js_config(self):
        android_js_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'android',
            'web',
            'js',
            'dataService.js'
        )
        
        if os.path.exists(android_js_path):
            with open(android_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_remote_api = 'remoteApiBase' in content
            has_llm_api = 'llmApiBase' in content
            
            self.assertTrue(has_remote_api, "dataService.js 应包含 remoteApiBase 配置")
            self.assertTrue(has_llm_api, "dataService.js 应包含 llmApiBase 配置")


if __name__ == '__main__':
    unittest.main(verbosity=2)
