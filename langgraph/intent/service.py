from typing import List, Dict, Any
from .intent_recognizer import IntentRecognizer
from .types import IntentType, IntentResult


class IntentService:
    def __init__(self, llm=None):
        self.recognizer = IntentRecognizer(llm)
        self.history: List[Dict[str, Any]] = []

    def analyze_intent(self, input_text: str) -> Dict[str, Any]:
        result = self.recognizer.recognize(input_text)
        response = {
            "success": True,
            "result": result.to_dict()
        }
        self.history.append(response)
        return response

    def analyze_batch(self, inputs: List[str]) -> Dict[str, Any]:
        results = []
        for inp in inputs:
            result = self.recognizer.recognize(inp)
            results.append(result.to_dict())
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }

    def get_intent_types(self) -> Dict[str, Any]:
        return {
            "success": True,
            "intent_types": [
                {"value": t.value, "description": self._get_intent_description(t)}
                for t in IntentType
            ]
        }

    def _get_intent_description(self, intent_type: IntentType) -> str:
        descriptions = {
            IntentType.GREETING: "用户问候，打招呼",
            IntentType.FAREWELL: "用户告别，结束对话",
            IntentType.GENERAL_CHAT: "通用聊天，闲聊",
            IntentType.CODE_QUERY: "代码相关问题：编程、调试、代码生成等",
            IntentType.DATA_ANALYSIS: "数据分析请求：统计、报表、可视化等",
            IntentType.KNOWLEDGE_QUERY: "知识查询：事实性问题、概念解释",
            IntentType.TASK_PLANNING: "任务规划：制定计划、步骤安排",
            IntentType.INFORMATION_SEARCH: "信息搜索：查找信息、资料",
            IntentType.CREATIVE_WRITING: "创意写作：文章、故事、邮件等",
            IntentType.UNKNOWN: "无法识别的意图"
        }
        return descriptions.get(intent_type, "未知意图")

    def get_history(self) -> Dict[str, Any]:
        return {
            "success": True,
            "history": self.history,
            "count": len(self.history)
        }

    def clear_history(self) -> Dict[str, Any]:
        self.history.clear()
        return {
            "success": True,
            "message": "History cleared"
        }
