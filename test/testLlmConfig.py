import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import yaml


class TestLlmConfig(unittest.TestCase):
    
    def setUp(self):
        self.config_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'config', 
            'llm.yml'
        )
    
    def test_config_file_exists(self):
        self.assertTrue(
            os.path.exists(self.config_path),
            f"配置文件不存在: {self.config_path}"
        )
    
    def test_config_is_valid_yaml(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            try:
                config = yaml.safe_load(f)
                self.assertIsNotNone(config)
            except yaml.YAMLError as e:
                self.fail(f"配置文件格式错误: {e}")
    
    def test_config_contains_required_keys(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self.assertIn('llm', config, "缺少 'llm' 配置块")
        self.assertIn('providers', config, "缺少 'providers' 配置块")
        
        llm_config = config['llm']
        self.assertIn('default_provider', llm_config, "缺少 'default_provider' 配置")
        self.assertIn('temperature', llm_config, "缺少 'temperature' 配置")
    
    def test_providers_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        providers = config['providers']
        
        self.assertIn('qwen', providers, "缺少 'qwen' 提供商配置")
        self.assertIn('deepseek', providers, "缺少 'deepseek' 提供商配置")
        
        for provider_name, provider_config in providers.items():
            self.assertIn('model', provider_config, 
                         f"{provider_name} 缺少 'model' 配置")
            self.assertIn('base_url', provider_config,
                         f"{provider_name} 缺少 'base_url' 配置")
            self.assertIn('api_key_env', provider_config,
                         f"{provider_name} 缺少 'api_key_env' 配置")
    
    def test_temperature_in_valid_range(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        temp = config['llm']['temperature']
        if temp is not None:
            self.assertGreaterEqual(temp, 0.0, "temperature 不能小于 0")
            self.assertLessEqual(temp, 2.0, "temperature 不能大于 2.0")
    
    def test_default_provider_is_valid(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        default_provider = config['llm']['default_provider']
        providers = config['providers']
        
        self.assertIn(
            default_provider, 
            providers,
            f"默认提供商 '{default_provider}' 不在 providers 列表中"
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
