import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))


class TestAppConfigIntegration(unittest.TestCase):
    
    def test_config_loader_imports(self):
        from config_loader import (
            get_llm_config,
            get_default_provider,
            get_llm_temperature,
            get_provider_config,
            get_model_name,
            get_api_key,
            get_base_url
        )
        self.assertTrue(callable(get_llm_config))
        self.assertTrue(callable(get_default_provider))
        self.assertTrue(callable(get_llm_temperature))
        self.assertTrue(callable(get_provider_config))
        self.assertTrue(callable(get_model_name))
        self.assertTrue(callable(get_api_key))
        self.assertTrue(callable(get_base_url))
    
    def test_app_imports_config_loader(self):
        import importlib.util
        app_path = os.path.join(os.path.dirname(__file__), '..', 'python', 'app.py')
        
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('from config_loader import', content, 
                     "app.py 未导入 config_loader")
        self.assertIn('get_llm_config', content,
                     "app.py 未使用 get_llm_config")
        self.assertIn('get_default_provider', content,
                     "app.py 未使用 get_default_provider")
        self.assertIn('get_llm_temperature', content,
                     "app.py 未使用 get_llm_temperature")
    
    def test_llm_config_structure(self):
        from config_loader import get_llm_config
        config = get_llm_config()
        
        self.assertIn('llm', config)
        self.assertIn('providers', config)
        self.assertIn('default_provider', config['llm'])
        self.assertIn('temperature', config['llm'])
        
        for provider_name, provider_config in config['providers'].items():
            self.assertIn('model', provider_config,
                         f"{provider_name} 缺少 model 配置")
            self.assertIn('base_url', provider_config,
                         f"{provider_name} 缺少 base_url 配置")
            self.assertIn('api_key_env', provider_config,
                         f"{provider_name} 缺少 api_key_env 配置")
    
    def test_provider_config_access(self):
        from config_loader import get_provider_config, get_model_name, get_base_url
        
        for provider in ['qwen', 'deepseek']:
            config = get_provider_config(provider)
            self.assertIsNotNone(config, f"{provider} 配置不应为 None")
            
            model = get_model_name(provider)
            self.assertIsNotNone(model, f"{provider} model 不应为 None")
            self.assertIsInstance(model, str)
            
            url = get_base_url(provider)
            self.assertIsNotNone(url, f"{provider} base_url 不应为 None")
            self.assertTrue(url.startswith('http'), 
                          f"{provider} base_url 应以 http 开头")
    
    def test_temperature_range(self):
        from config_loader import get_llm_temperature
        temp = get_llm_temperature()
        self.assertGreaterEqual(temp, 0.0, "temperature 不能小于 0")
        self.assertLessEqual(temp, 2.0, "temperature 不能大于 2")
    
    def test_removed_hardcoded_values(self):
        app_path = os.path.join(os.path.dirname(__file__), '..', 'python', 'app.py')
        
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertNotIn('QWEN_MODEL =', content,
                        "不应有硬编码的 QWEN_MODEL 变量")
        self.assertNotIn('DEEPSEEK_MODEL =', content,
                        "不应有硬编码的 DEEPSEEK_MODEL 变量")
        self.assertNotIn('QWEN_BASE_URL =', content,
                        "不应有硬编码的 QWEN_BASE_URL 变量")
        self.assertNotIn('DEEPSEEK_BASE_URL =', content,
                        "不应有硬编码的 DEEPSEEK_BASE_URL 变量")
        self.assertNotIn('temperature=0.7', content,
                        "不应有硬编码的 temperature=0.7")


if __name__ == '__main__':
    unittest.main(verbosity=2)
