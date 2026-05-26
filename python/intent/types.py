from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict


class IntentType(Enum):
    GREETING = "greeting"
    FAREWELL = "farewell"
    GENERAL_CHAT = "general_chat"
    CODE_QUERY = "code_query"
    DATA_ANALYSIS = "data_analysis"
    KNOWLEDGE_QUERY = "knowledge_query"
    TASK_PLANNING = "task_planning"
    INFORMATION_SEARCH = "information_search"
    CREATIVE_WRITING = "creative_writing"
    UNKNOWN = "unknown"


@dataclass
class IntentSubtask:
    name: str
    description: str
    priority: str = "normal"
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class IntentResult:
    intent: IntentType
    confidence: float
    reason: str
    entities: Dict[str, Any] = field(default_factory=dict)
    subtasks: List[IntentSubtask] = field(default_factory=list)
    original_input: str = ""
    analyzed_at: str = ""
    llm_used: bool = False
    llm_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "reason": self.reason,
            "entities": self.entities,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "original_input": self.original_input,
            "analyzed_at": self.analyzed_at,
            "llm_used": self.llm_used,
            "llm_details": self.llm_details
        }
