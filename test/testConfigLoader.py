import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import config_loader as cl


class TestConfigLoader(unittest.TestCase):
    
    def setUp(self):
        cl._config_cache = {}
    
    def test_load_llm_config(self):
        config = cl.load_config('llm')
        self.assertIsNotNone(config)
        self.assertIn('llm', config)
        self.assertIn('providers', config)
    
    def test_get_llm_config_returns_dict(self):
        config = cl.get_llm_config()
        self.assertIsInstance(config, dict)
        self.assertIn('llm', config)
        self.assertIn('providers', config)
    
    def test_get_default_provider(self):
        provider = cl.get_default_provider()
        self.assertIsInstance(provider, str)
        self.assertIn(provider, ['qwen', 'deepseek'])
    
    def test_get_llm_temperature(self):
        temp = cl.get_llm_temperature()
        self.assertIsInstance(temp, (int, float))
        self.assertGreaterEqual(temp, 0.0)
        self.assertLessEqual(temp, 2.0)
    
    def test_get_provider_config_qwen(self):
        config = cl.get_provider_config('qwen')
        self.assertIsNotNone(config)
        self.assertIn('model', config)
        self.assertIn('base_url', config)
        self.assertIn('api_key_env', config)
    
    def test_get_provider_config_deepseek(self):
        config = cl.get_provider_config('deepseek')
        self.assertIsNotNone(config)
        self.assertIn('model', config)
        self.assertIn('base_url', config)
        self.assertIn('api_key_env', config)
    
    def test_get_model_name_qwen(self):
        model = cl.get_model_name('qwen')
        self.assertIsNotNone(model)
        self.assertIsInstance(model, str)
    
    def test_get_model_name_deepseek(self):
        model = cl.get_model_name('deepseek')
        self.assertIsNotNone(model)
        self.assertIsInstance(model, str)
    
    def test_get_base_url_qwen(self):
        url = cl.get_base_url('qwen')
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith('http'))
    
    def test_get_base_url_deepseek(self):
        url = cl.get_base_url('deepseek')
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith('http'))
    
    def test_unknown_provider_returns_none(self):
        config = cl.get_provider_config('unknown_provider')
        self.assertIsNone(config)
        
        model = cl.get_model_name('unknown_provider')
        self.assertIsNone(model)
        
        url = cl.get_base_url('unknown_provider')
        self.assertIsNone(url)
    
    def test_config_merges_yaml_with_env_defaults(self):
        config = cl.get_llm_config()
        self.assertIsNotNone(config.get('llm'))
        self.assertIsNotNone(config.get('providers'))
        for provider_name in ['qwen', 'deepseek']:
            provider = config['providers'].get(provider_name, {})
            self.assertIn('model', provider)
            self.assertIn('base_url', provider)


if __name__ == '__main__':
    unittest.main(verbosity=2)
