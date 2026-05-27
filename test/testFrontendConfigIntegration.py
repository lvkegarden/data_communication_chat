import os
import sys
import unittest
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))


class TestFrontendConfigIntegration(unittest.TestCase):
    
    def setUp(self):
        self.web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
        self.config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'web-config.js')
    
    def test_web_config_file_exists(self):
        self.assertTrue(os.path.exists(self.config_file),
                       f"前端配置文件不存在: {self.config_file}")
    
    def test_html_files_import_web_config(self):
        html_files = [
            ('chat.html', 'chat.html'),
            ('product_agent.html', 'product_agent.html'),
            ('collect.html', 'collect.html'),
            ('index.html', 'index.html'),
            ('intent_test.html', 'intent_test.html')
        ]
        
        for filename, display_name in html_files:
            filepath = os.path.join(self.web_dir, filename)
            if not os.path.exists(filepath):
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_config_import = 'web-config.js' in content
            has_appconfig = 'window.AppConfig' in content or 'AppConfig.' in content
            
            self.assertTrue(has_config_import,
                          f"{display_name} 未引入 web-config.js")
            self.assertTrue(has_appconfig,
                          f"{display_name} 未使用 AppConfig 配置")
    
    def test_html_files_removed_hardcoded_localhost(self):
        html_files = [
            'chat.html',
            'product_agent.html',
            'collect.html',
            'index.html',
            'intent_test.html'
        ]
        
        for filename in html_files:
            filepath = os.path.join(self.web_dir, filename)
            if not os.path.exists(filepath):
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_localhost_8080 = 'localhost:8080' in content
            has_localhost_5001 = 'localhost:5001' in content
            
            self.assertFalse(has_localhost_8080,
                           f"{filename} 仍包含硬编码的 localhost:8080")
            self.assertFalse(has_localhost_5001,
                           f"{filename} 仍包含硬编码的 localhost:5001")
    
    def test_html_files_use_appconfig_api_urls(self):
        html_files = [
            'chat.html',
            'product_agent.html',
            'collect.html',
            'index.html',
            'intent_test.html'
        ]
        
        for filename in html_files:
            filepath = os.path.join(self.web_dir, filename)
            if not os.path.exists(filepath):
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_java_config = 'AppConfig.api.javaBaseUrl' in content
            has_python_config = 'AppConfig.api.pythonBaseUrl' in content
            
            self.assertTrue(has_java_config or has_python_config,
                          f"{filename} 未使用 AppConfig.api 配置")
    
    def test_android_data_service_uses_config_or_has_comments(self):
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
            
            self.assertTrue(has_remote_api,
                           "dataService.js 应包含 remoteApiBase 配置")
            self.assertTrue(has_llm_api,
                           "dataService.js 应包含 llmApiBase 配置")
    
    def test_web_config_has_correct_structure(self):
        with open(self.config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('window.AppConfig', content)
        self.assertIn('javaBaseUrl', content)
        self.assertIn('pythonBaseUrl', content)
        self.assertIn('http://localhost:8080', content)
        self.assertIn('http://localhost:5001', content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
