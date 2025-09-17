"""
OpenAI Provider Implementation
Handles all OpenAI API interactions with gpt-4o-mini as default
"""
import os
import json
from typing import Dict, List, Any, Optional, Union
from openai import AsyncOpenAI
from .base import BaseAIProvider, AIModel, AIResponse, AIMessage

class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None, model: AIModel = AIModel.GPT_4O_MINI, **kwargs):
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        super().__init__(api_key, model, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def chat_completion(
        self,
        messages: List[AIMessage],
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = "auto",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Generate chat completion with OpenAI API"""
        
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            message_dict = {
                "role": msg.role,
                "content": msg.content
            }
            if msg.name:
                message_dict["name"] = msg.name
            if msg.function_call:
                message_dict["function_call"] = msg.function_call
            openai_messages.append(message_dict)
        
        # Prepare request parameters
        request_params = {
            "model": self.model.value,
            "messages": openai_messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            request_params["max_tokens"] = max_tokens
        
        if functions:
            request_params["functions"] = functions
            request_params["function_call"] = function_call
        
        # Make API call
        try:
            response = await self.client.chat.completions.create(**request_params)
            
            # Extract response content
            choice = response.choices[0]
            content = choice.message.content or ""
            
            # Extract function calls if present
            function_calls = None
            if choice.message.function_call:
                function_calls = [{
                    "name": choice.message.function_call.name,
                    "arguments": json.loads(choice.message.function_call.arguments)
                }]
            
            # Extract usage information
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            return AIResponse(
                content=content,
                model=self.model.value,
                usage=usage,
                function_calls=function_calls,
                metadata={
                    "finish_reason": choice.finish_reason,
                    "response_id": response.id
                }
            )
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def extract_entities(
        self,
        text: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Extract structured entities using OpenAI with JSON mode"""
        
        system_prompt = f"""You are an expert at extracting structured information from text.
        
Extract the following information from the provided text and return it as valid JSON:
{json.dumps(schema, indent=2)}

Rules:
- Return only valid JSON
- Use null for missing values
- Be precise and accurate
- Don't make assumptions"""
        
        messages = [
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=text)
        ]
        
        response = await self.chat_completion(
            messages=messages,
            temperature=0.1,  # Low temperature for consistency
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON response", "raw": response.content}
    
    async def generate_email(
        self,
        template: str,
        context: Dict[str, Any],
        tone: str = "professional",
        **kwargs
    ) -> str:
        """Generate personalized email content"""
        
        system_prompt = f"""You are an expert sales email writer. Generate a personalized email based on the template and context.

Tone: {tone}
Template: {template}

Context: {json.dumps(context, indent=2)}

Guidelines:
- Maintain the core message of the template
- Personalize using the provided context
- Keep the tone {tone}
- Make it engaging and actionable
- Include a clear call-to-action
- Keep it concise but complete"""
        
        messages = [
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content="Generate the personalized email content.")
        ]
        
        response = await self.chat_completion(
            messages=messages,
            temperature=0.8,  # Higher creativity for email generation
            max_tokens=1000
        )
        
        return response.content
    
    async def analyze_sentiment(
        self,
        text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze sentiment and intent"""
        
        system_prompt = """Analyze the sentiment and intent of the provided text. Return a JSON object with:
- sentiment: "positive", "negative", "neutral"
- confidence: 0.0 to 1.0
- intent: "inquiry", "complaint", "praise", "request", "other"
- urgency: "low", "medium", "high"
- key_topics: array of main topics mentioned
- suggested_action: recommended next step"""
        
        messages = [
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=text)
        ]
        
        response = await self.chat_completion(
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse sentiment analysis"}
    
    async def summarize_conversation(
        self,
        messages: List[AIMessage],
        **kwargs
    ) -> str:
        """Summarize conversation history"""
        
        # Convert messages to text
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in messages
        ])
        
        system_prompt = """Summarize this conversation focusing on:
- Key points discussed
- Decisions made
- Action items
- Next steps
- Important details for follow-up

Keep the summary concise but comprehensive."""
        
        messages = [
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=conversation_text)
        ]
        
        response = await self.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        
        return response.content
    
    def _get_max_context(self) -> int:
        """Get maximum context length for the model"""
        context_limits = {
            AIModel.GPT_4O_MINI: 128000,
            AIModel.GPT_4O: 128000,
            AIModel.GPT_3_5_TURBO: 16385,
        }
        return context_limits.get(self.model, 128000)
    
    def _get_cost_info(self) -> Dict[str, float]:
        """Get cost information for the model (per 1K tokens)"""
        costs = {
            AIModel.GPT_4O_MINI: {"input": 0.00015, "output": 0.0006},
            AIModel.GPT_4O: {"input": 0.005, "output": 0.015},
            AIModel.GPT_3_5_TURBO: {"input": 0.0005, "output": 0.0015},
        }
        return costs.get(self.model, {"input": 0.00015, "output": 0.0006})
