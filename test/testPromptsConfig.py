import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

import config_loader as cl


class TestPromptsConfig(unittest.TestCase):
    
    def setUp(self):
        cl._config_cache = {}
    
    def test_config_file_exists(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'config',
            'prompts.yml'
        )
        self.assertTrue(
            os.path.exists(config_path),
            f"配置文件不存在: {config_path}"
        )
    
    def test_load_prompts_config(self):
        config = cl.load_config('prompts')
        self.assertIsNotNone(config)
        self.assertIn('system_prompts', config)
        self.assertIn('intent_keywords', config)
    
    def test_get_prompts_config(self):
        config = cl.get_prompts_config()
        self.assertIsInstance(config, dict)
        self.assertIn('system_prompts', config)
        self.assertIn('intent_keywords', config)
    
    def test_system_prompts_structure(self):
        config = cl.get_prompts_config()
        prompts = config['system_prompts']
        
        required_prompts = [
            'product_introduction',
            'competitor_analysis', 
            'product_query',
            'general_chat'
        ]
        
        for prompt_name in required_prompts:
            self.assertIn(prompt_name, prompts,
                         f"缺少系统提示词: {prompt_name}")
            self.assertIsInstance(prompts[prompt_name], str)
            self.assertTrue(len(prompts[prompt_name]) > 0,
                          f"系统提示词为空: {prompt_name}")
    
    def test_get_system_prompt(self):
        prompt = cl.get_system_prompt('product_introduction')
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)
        
        prompt = cl.get_system_prompt('competitor_analysis')
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)
        
        prompt = cl.get_system_prompt('unknown_intent')
        self.assertIsInstance(prompt, str)
    
    def test_intent_keywords_structure(self):
        config = cl.get_prompts_config()
        keywords = config['intent_keywords']
        
        required_intents = [
            'greeting',
            'farewell',
            'code_query',
            'competitor_analysis',
            'product_introduction',
            'product_query',
            'data_analysis',
            'knowledge_query'
        ]
        
        for intent_name in required_intents:
            self.assertIn(intent_name, keywords,
                         f"缺少意图关键词配置: {intent_name}")
            
            intent_config = keywords[intent_name]
            self.assertIn('keywords', intent_config,
                         f"{intent_name} 缺少 keywords 配置")
            self.assertIn('confidence', intent_config,
                         f"{intent_name} 缺少 confidence 配置")
            self.assertIn('reason', intent_config,
                         f"{intent_name} 缺少 reason 配置")
            
            self.assertIsInstance(intent_config['keywords'], list)
            self.assertIsInstance(intent_config['confidence'], (int, float))
            self.assertIsInstance(intent_config['reason'], str)
    
    def test_get_intent_keywords(self):
        greeting = cl.get_intent_keywords('greeting')
        self.assertIsNotNone(greeting)
        self.assertIn('keywords', greeting)
        self.assertIn('你好', greeting['keywords'])
        
        farewell = cl.get_intent_keywords('farewell')
        self.assertIsNotNone(farewell)
        self.assertIn('再见', farewell['keywords'])
        
        unknown = cl.get_intent_keywords('unknown_intent')
        self.assertIsNone(unknown)
    
    def test_get_all_intent_keywords(self):
        all_keywords = cl.get_all_intent_keywords()
        self.assertIsInstance(all_keywords, dict)
        self.assertTrue(len(all_keywords) > 0)
        
        for intent_name, config in all_keywords.items():
            self.assertIn('keywords', config)
            self.assertIn('confidence', config)
            self.assertIn('reason', config)
    
    def test_confidence_values_are_valid(self):
        all_keywords = cl.get_all_intent_keywords()
        
        for intent_name, config in all_keywords.items():
            confidence = config.get('confidence', 0)
            self.assertGreaterEqual(confidence, 0.0,
                                  f"{intent_name} confidence 不能小于 0")
            self.assertLessEqual(confidence, 1.0,
                               f"{intent_name} confidence 不能大于 1")
    
    def test_keywords_lists_are_not_empty(self):
        all_keywords = cl.get_all_intent_keywords()
        
        for intent_name, config in all_keywords.items():
            keywords = config.get('keywords', [])
            self.assertTrue(len(keywords) > 0,
                          f"{intent_name} 关键词列表不能为空")


if __name__ == '__main__':
    unittest.main(verbosity=2)
