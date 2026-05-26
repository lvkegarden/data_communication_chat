import json
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from .types import IntentType, IntentResult, IntentSubtask


class IntentRecognizer:
    def __init__(self, llm=None):
        self.llm = llm

    def recognize(self, input_text: str) -> IntentResult:
        entities = self._extract_entities(input_text)
        intent_info = self._classify_intent(input_text, entities)
        
        intent_info.llm_used = False
        intent_info.llm_details = {
            "llm_available": bool(self.llm),
            "rule_intent": intent_info.intent.value,
            "rule_confidence": intent_info.confidence,
            "llm_called": False,
            "llm_intent": None,
            "llm_confidence": 0.0,
            "selected_source": "rule"
        }
        
        if self.llm and intent_info.intent != IntentType.GREETING and intent_info.intent != IntentType.FAREWELL:
            intent_info.llm_details["llm_called"] = True
            llm_result = self._llm_recognize(input_text)
            
            if llm_result:
                llm_result.llm_used = True
                llm_result.llm_details = {
                    "llm_available": True,
                    "rule_intent": intent_info.intent.value,
                    "rule_confidence": intent_info.confidence,
                    "llm_called": True,
                    "llm_intent": llm_result.intent.value,
                    "llm_confidence": llm_result.confidence,
                    "selected_source": "llm" if llm_result.confidence > intent_info.confidence else "rule"
                }
                
                if llm_result.confidence > intent_info.confidence:
                    return llm_result
                else:
                    intent_info.llm_used = True
                    intent_info.llm_details["llm_intent"] = llm_result.intent.value
                    intent_info.llm_details["llm_confidence"] = llm_result.confidence
                    intent_info.llm_details["selected_source"] = "rule"
        
        return intent_info

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        entities = {}
        
        date_patterns = [
            r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日号]?',
            r'今天',
            r'明天',
            r'后天',
            r'昨天',
            r'前天',
            r'下周[一二三四五六日天]',
            r'上[个]?周[一二三四五六日天]',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                entities['dates'] = list(set(matches))
        
        keywords = {
            'python': ['python', 'py', 'Python', 'PYTHON'],
            'java': ['java', 'Java', 'JAVA'],
            'javascript': ['javascript', 'js', 'JS', 'JavaScript'],
            'typescript': ['typescript', 'ts', 'TS', 'TypeScript'],
            'rust': ['rust', 'Rust', 'RUST'],
            'go': ['go', 'Go', 'Golang', 'golang'],
            'mysql': ['mysql', 'MySQL', 'MYSQL', '数据库'],
            'sql': ['sql', 'SQL', '查询'],
            'excel': ['excel', 'Excel', '表格'],
            '图表': ['图表', '图', 'chart', 'Chart'],
            '统计': ['统计', '分析', '统计分析'],
        }
        
        for entity_name, patterns in keywords.items():
            for pattern in patterns:
                if pattern in text:
                    entities['technologies'] = entities.get('technologies', []) + [entity_name]
                    break
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            entities['emails'] = list(set(emails))
        
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, text)
        if urls:
            entities['urls'] = list(set(urls))
        
        return entities

    def _classify_intent(self, text: str, entities: Dict[str, Any]) -> IntentResult:
        text_lower = text.lower()
        
        greeting_patterns = ['你好', '您好', 'hi', 'hello', '嗨', '嘿', '早上好', '下午好', '晚上好']
        if any(p in text_lower for p in greeting_patterns) and len(text) < 20:
            return IntentResult(
                intent=IntentType.GREETING,
                confidence=0.95,
                reason="检测到问候语",
                entities=entities,
                subtasks=[],
                original_input=text,
                analyzed_at=datetime.now().isoformat()
            )
        
        farewell_patterns = ['再见', '拜拜', 'bye', '回头见', '下次见', '晚安', '拜拜了']
        if any(p in text_lower for p in farewell_patterns) and len(text) < 20:
            return IntentResult(
                intent=IntentType.FAREWELL,
                confidence=0.95,
                reason="检测到告别语",
                entities=entities,
                subtasks=[],
                original_input=text,
                analyzed_at=datetime.now().isoformat()
            )
        
        code_patterns = ['代码', '程序', '函数', '类', 'bug', '错误', '调试', '报错', '运行', '实现', '写个', '编写', '优化']
        techs = entities.get('technologies', [])
        code_techs = ['python', 'java', 'javascript', 'typescript', 'rust', 'go', 'mysql', 'sql']
        
        if any(t in code_techs for t in techs) or any(p in text for p in code_patterns):
            subtasks = self._generate_code_subtasks(text, techs)
            return IntentResult(
                intent=IntentType.CODE_QUERY,
                confidence=0.85,
                reason="检测到代码相关术语或编程语言",
                entities=entities,
                subtasks=subtasks,
                original_input=text,
                analyzed_at=datetime.now().isoformat()
            )
        
        data_patterns = ['分析', '统计', '数据', '报表', '报告', '趋势', '增长', '下降', '对比', 'excel', '表格', '图表']
        if any(p in text_lower for p in data_patterns):
            subtasks = self._generate_data_subtasks(text)
            return IntentResult(
                intent=IntentType.DATA_ANALYSIS,
                confidence=0.80,
                reason="检测到数据分析相关术语",
                entities=entities,
                subtasks=subtasks,
                original_input=text,
                analyzed_at=datetime.now().isoformat()
            )
        
        task_patterns = ['计划', '安排', '步骤', '流程', '怎么', '如何', '怎样', '方案', '策略', '建议']
        if any(p in text for p in task_patterns):
            subtasks = self._generate_task_subtasks(text)
            return IntentResult(
                intent=IntentType.TASK_PLANNING,
                confidence=0.75,
                reason="检测到任务规划相关请求",
                entities=entities,
                subtasks=subtasks,
                original_input=text,
                analyzed_at=datetime.now().isoformat()
            )
        
        search_patterns = ['搜索', '查找', '查询', '找', '什么是', '是什么', '哪里', '怎么', '为什么', '何时', '何地', '何人']
        if any(p in text for p in search_patterns):
            subtasks = self._generate_search_subtasks(text)
            return IntentResult(
                intent=IntentType.INFORMATION_SEARCH,
                confidence=0.70,
                reason="检测到信息查询请求",
                entities=entities,
                subtasks=subtasks,
                original_input=text,
                analyzed_at=datetime.now().isoformat()
            )
        
        creative_patterns = ['写', '创作', '生成', '制作', '设计', '文章', '故事', '诗歌', '邮件', '报告', '文案', '总结']
        if any(p in text for p in creative_patterns):
            subtasks = self._generate_creative_subtasks(text)
            return IntentResult(
                intent=IntentType.CREATIVE_WRITING,
                confidence=0.65,
                reason="检测到创意写作相关请求",
                entities=entities,
                subtasks=subtasks,
                original_input=text,
                analyzed_at=datetime.now().isoformat()
            )
        
        knowledge_patterns = ['是什么', '为什么', '怎么回事', '解释', '说明', '原理', '机制', '理论']
        if any(p in text for p in knowledge_patterns):
            subtasks = self._generate_knowledge_subtasks(text)
            return IntentResult(
                intent=IntentType.KNOWLEDGE_QUERY,
                confidence=0.60,
                reason="检测到知识查询请求",
                entities=entities,
                subtasks=subtasks,
                original_input=text,
                analyzed_at=datetime.now().isoformat()
            )
        
        return IntentResult(
            intent=IntentType.GENERAL_CHAT,
            confidence=0.50,
            reason="未匹配到特定意图，归类为通用聊天",
            entities=entities,
            subtasks=[],
            original_input=text,
            analyzed_at=datetime.now().isoformat()
        )

    def _generate_code_subtasks(self, text: str, techs: List[str]) -> List[IntentSubtask]:
        subtasks = []
        
        if 'bug' in text.lower() or '错误' in text or '报错' in text:
            subtasks.append(IntentSubtask(
                name="错误分析",
                description="分析错误信息和上下文",
                priority="high"
            ))
            subtasks.append(IntentSubtask(
                name="调试建议",
                description="提供调试步骤和修复方案",
                priority="high",
                dependencies=["错误分析"]
            ))
        
        elif '优化' in text or '改进' in text:
            subtasks.append(IntentSubtask(
                name="性能评估",
                description="评估当前代码性能瓶颈",
                priority="high"
            ))
            subtasks.append(IntentSubtask(
                name="优化方案",
                description="提供具体优化建议",
                priority="high",
                dependencies=["性能评估"]
            ))
        
        elif '写' in text or '实现' in text or '创建' in text:
            subtasks.append(IntentSubtask(
                name="需求分析",
                description="理解功能需求和技术要求",
                priority="high"
            ))
            subtasks.append(IntentSubtask(
                name="代码实现",
                description="编写符合需求的代码",
                priority="high",
                dependencies=["需求分析"]
            ))
            subtasks.append(IntentSubtask(
                name="代码说明",
                description="解释代码逻辑和使用方法",
                priority="medium",
                dependencies=["代码实现"]
            ))
        
        else:
            subtasks.append(IntentSubtask(
                name="问题理解",
                description="分析用户的代码问题",
                priority="high"
            ))
            subtasks.append(IntentSubtask(
                name="解决方案",
                description="提供问题解答或代码示例",
                priority="high",
                dependencies=["问题理解"]
            ))
        
        return subtasks

    def _generate_data_subtasks(self, text: str) -> List[IntentSubtask]:
        subtasks = [
            IntentSubtask(
                name="数据理解",
                description="理解数据来源和分析目标",
                priority="high"
            ),
            IntentSubtask(
                name="分析方法选择",
                description="选择合适的数据分析方法",
                priority="high",
                dependencies=["数据理解"]
            ),
            IntentSubtask(
                name="结果呈现",
                description="以图表或报告形式呈现分析结果",
                priority="medium",
                dependencies=["分析方法选择"]
            )
        ]
        
        if '对比' in text:
            subtasks.insert(1, IntentSubtask(
                name="对比维度设计",
                description="设计数据对比的维度和指标",
                priority="high",
                dependencies=["数据理解"]
            ))
        
        return subtasks

    def _generate_task_subtasks(self, text: str) -> List[IntentSubtask]:
        return [
            IntentSubtask(
                name="目标拆解",
                description="将整体目标拆解为可执行的子任务",
                priority="high"
            ),
            IntentSubtask(
                name="优先级排序",
                description="确定各任务的执行顺序和优先级",
                priority="high",
                dependencies=["目标拆解"]
            ),
            IntentSubtask(
                name="时间规划",
                description="为各任务分配合理的时间",
                priority="medium",
                dependencies=["优先级排序"]
            ),
            IntentSubtask(
                name="风险评估",
                description="识别潜在风险并制定应对方案",
                priority="medium",
                dependencies=["时间规划"]
            )
        ]

    def _generate_search_subtasks(self, text: str) -> List[IntentSubtask]:
        return [
            IntentSubtask(
                name="关键词提取",
                description="从查询中提取核心关键词",
                priority="high"
            ),
            IntentSubtask(
                name="信息检索",
                description="根据关键词检索相关信息",
                priority="high",
                dependencies=["关键词提取"]
            ),
            IntentSubtask(
                name="结果整理",
                description="整理并总结检索到的信息",
                priority="medium",
                dependencies=["信息检索"]
            ),
            IntentSubtask(
                name="答案生成",
                description="生成准确完整的回答",
                priority="high",
                dependencies=["结果整理"]
            )
        ]

    def _generate_creative_subtasks(self, text: str) -> List[IntentSubtask]:
        return [
            IntentSubtask(
                name="需求分析",
                description="理解写作目标和受众",
                priority="high"
            ),
            IntentSubtask(
                name="大纲设计",
                description="设计内容结构和大纲",
                priority="high",
                dependencies=["需求分析"]
            ),
            IntentSubtask(
                name="内容创作",
                description="撰写完整的内容",
                priority="high",
                dependencies=["大纲设计"]
            ),
            IntentSubtask(
                name="润色优化",
                description="优化表达和格式",
                priority="medium",
                dependencies=["内容创作"]
            )
        ]

    def _generate_knowledge_subtasks(self, text: str) -> List[IntentSubtask]:
        return [
            IntentSubtask(
                name="概念定位",
                description="确定需要解释的核心概念",
                priority="high"
            ),
            IntentSubtask(
                name="知识检索",
                description="检索相关知识背景",
                priority="high",
                dependencies=["概念定位"]
            ),
            IntentSubtask(
                name="解释说明",
                description="用易懂的方式解释概念",
                priority="high",
                dependencies=["知识检索"]
            ),
            IntentSubtask(
                name="示例补充",
                description="提供相关示例帮助理解",
                priority="medium",
                dependencies=["解释说明"]
            )
        ]

    def _llm_recognize(self, input_text: str) -> IntentResult:
        if not self.llm:
            return None
        
        system_prompt = """你是一个专业的意图识别助手。请分析用户输入，识别其意图并拆解为子任务。

可用的意图类型：
- greeting: 问候
- farewell: 告别
- general_chat: 通用聊天
- code_query: 代码相关（编程、调试、代码生成等）
- data_analysis: 数据分析
- knowledge_query: 知识查询
- task_planning: 任务规划
- information_search: 信息搜索
- creative_writing: 创意写作
- unknown: 未知

请以JSON格式返回，包含以下字段：
{
    "intent": "意图类型",
    "confidence": 置信度(0.0-1.0),
    "reason": "判断理由",
    "entities": {"提取的实体": "值"},
    "subtasks": [
        {"name": "子任务名", "description": "描述", "priority": "high/medium/low", "dependencies": ["前置子任务名"]}
    ]
}"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=input_text)
        ]
        
        try:
            response = self.llm.invoke(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
                
                intent_map = {t.value: t for t in IntentType}
                intent = intent_map.get(data.get('intent'), IntentType.UNKNOWN)
                
                subtasks = []
                for st in data.get('subtasks', []):
                    subtasks.append(IntentSubtask(
                        name=st.get('name', ''),
                        description=st.get('description', ''),
                        priority=st.get('priority', 'normal'),
                        dependencies=st.get('dependencies', [])
                    ))
                
                return IntentResult(
                    intent=intent,
                    confidence=float(data.get('confidence', 0.5)),
                    reason=data.get('reason', ''),
                    entities=data.get('entities', {}),
                    subtasks=subtasks,
                    original_input=input_text,
                    analyzed_at=datetime.now().isoformat()
                )
        except Exception as e:
            print(f"LLM recognition error: {e}")
        
        return None
