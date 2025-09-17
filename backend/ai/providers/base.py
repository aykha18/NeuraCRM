"""
Base AI Provider Interface
Defines the contract for all AI providers (OpenAI, Anthropic, Ollama, etc.)
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

class AIModel(Enum):
    # OpenAI Models
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Anthropic Models
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Ollama Models
    LLAMA_3_1_8B = "llama3.1:8b-instruct"
    LLAMA_3_1_70B = "llama3.1:70b-instruct"
    QWEN2_5_32B = "qwen2.5:32b-instruct"

@dataclass
class AIResponse:
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    function_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AIMessage:
    role: str  # system, user, assistant, function
    content: str
    name: Optional[str] = None  # for function calls
    function_call: Optional[Dict[str, Any]] = None

class BaseAIProvider(ABC):
    """Base class for all AI providers"""
    
    def __init__(self, api_key: str, model: AIModel, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[AIMessage],
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = "auto",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Generate chat completion with optional function calling"""
        pass
    
    @abstractmethod
    async def extract_entities(
        self,
        text: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Extract structured entities from text"""
        pass
    
    @abstractmethod
    async def generate_email(
        self,
        template: str,
        context: Dict[str, Any],
        tone: str = "professional",
        **kwargs
    ) -> str:
        """Generate personalized email content"""
        pass
    
    @abstractmethod
    async def analyze_sentiment(
        self,
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze sentiment and intent"""
        pass
    
    @abstractmethod
    async def summarize_conversation(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> str:
        """Summarize conversation history"""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "provider": self.__class__.__name__,
            "model": self.model.value,
            "supports_functions": True,
            "max_context": self._get_max_context(),
            "cost_per_1k_tokens": self._get_cost_info()
        }
    
    @abstractmethod
    def _get_max_context(self) -> int:
        """Get maximum context length for the model"""
        pass
    
    @abstractmethod
    def _get_cost_info(self) -> Dict[str, float]:
        """Get cost information for the model"""
        pass
