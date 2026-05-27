import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

from intent_router import IntentRouter, IntentType


class TestIntentRouterConfig(unittest.TestCase):
    
    def setUp(self):
        self.router = IntentRouter()
    
    def test_router_loads_keyword_configs(self):
        self.assertTrue(hasattr(self.router, 'intent_keywords'))
        self.assertIsInstance(self.router.intent_keywords, dict)
        self.assertTrue(len(self.router.intent_keywords) > 0)
    
    def test_classify_greeting(self):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.content = "你好"
        
        result = self.router.classify([msg])
        self.assertEqual(result.intent, IntentType.GREETING)
        self.assertEqual(result.confidence, 0.9)
    
    def test_classify_greeting_short_only(self):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.content = "你好，我想查询一个产品信息，这个产品非常复杂"
        
        result = self.router.classify([msg])
        self.assertNotEqual(result.intent, IntentType.GREETING)
    
    def test_classify_farewell(self):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.content = "再见"
        
        result = self.router.classify([msg])
        self.assertEqual(result.intent, IntentType.FAREWELL)
        self.assertEqual(result.confidence, 0.9)
    
    def test_classify_code_query(self):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.content = "帮我看一下这个Python代码有什么问题"
        
        result = self.router.classify([msg])
        self.assertEqual(result.intent, IntentType.CODE_QUERY)
    
    def test_classify_product_introduction(self):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.content = "帮我生成RG-AP820C的产品介绍"
        
        result = self.router.classify([msg])
        self.assertEqual(result.intent, IntentType.PRODUCT_INTRODUCTION)
    
    def test_classify_competitor_analysis(self):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.content = "帮我做一下S5735-L的竞品分析"
        
        result = self.router.classify([msg])
        self.assertEqual(result.intent, IntentType.COMPETITOR_ANALYSIS)
    
    def test_classify_product_query(self):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.content = "查看所有产品列表"
        
        result = self.router.classify([msg])
        self.assertEqual(result.intent, IntentType.PRODUCT_QUERY)
    
    def test_classify_data_analysis(self):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.content = "分析一下我们有多少个产品"
        
        result = self.router.classify([msg])
        self.assertEqual(result.intent, IntentType.DATA_ANALYSIS)
    
    def test_classify_knowledge_query(self):
        from unittest.mock import MagicMock
        msg = '什么是交换机？'
        result = self.router.classify([msg])
        self.assertEqual(result.intent, IntentType.KNOWLEDGE_QUERY)
    
    def test_classify_general_chat(self):
        from unittest.mock import MagicMock
        msg = MagicMock()
        msg.content = "今天天气真好"
        
        result = self.router.classify([msg])
        self.assertEqual(result.intent, IntentType.GENERAL_CHAT)
    
    def test_empty_messages_returns_unknown(self):
        result = self.router.classify([])
        self.assertEqual(result.intent, IntentType.UNKNOWN)
    
    def test_app_uses_configured_system_prompts(self):
        app_path = os.path.join(os.path.dirname(__file__), '..', 'python', 'app.py')
        
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('get_system_prompt', content,
                     "app.py 应使用 get_system_prompt 函数")
        self.assertNotIn('你是一个专业的数通产品分析师，擅长撰写清晰、有吸引力的产品介绍', content,
                        "app.py 不应有硬编码的系统提示词")


if __name__ == '__main__':
    unittest.main(verbosity=2)
