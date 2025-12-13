"""
Streamware LLM Manager
Manages LLM providers (Ollama, OpenAI, Anthropic) with runtime switching
"""

import httpx
import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("streamware.llm")


class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    finish_reason: str = ""
    error: Optional[str] = None


class LLMManager:
    """Manages multiple LLM providers with runtime switching"""
    
    def __init__(self):
        self.providers: Dict[str, Dict] = {}
        self.active_provider: str = "ollama"
        self.active_model: str = "llama2"
        self.http_client: Optional[httpx.AsyncClient] = None
        self._service_status: Dict[str, Dict] = {}
        
        logger.info("🤖 LLMManager initialized")
    
    async def start(self):
        """Initialize HTTP client"""
        self.http_client = httpx.AsyncClient(timeout=60.0)
        logger.info("🔗 LLM HTTP client started")
    
    async def stop(self):
        """Cleanup"""
        if self.http_client:
            await self.http_client.aclose()
        logger.info("🔌 LLM HTTP client stopped")
    
    def register_provider(self, provider_id: str, config: Dict):
        """Register an LLM provider"""
        self.providers[provider_id] = config
        logger.info(f"📝 LLM provider registered: {provider_id}")
    
    def set_active(self, provider_id: str, model: str = None):
        """Set active LLM provider and model"""
        if provider_id in self.providers:
            self.active_provider = provider_id
            if model:
                self.active_model = model
            elif "default_model" in self.providers[provider_id]:
                self.active_model = self.providers[provider_id]["default_model"]
            
            logger.info(f"🎯 Active LLM: {provider_id}/{self.active_model}")
            return True
        return False
    
    def get_active(self) -> Dict:
        """Get active provider config"""
        return {
            "provider": self.active_provider,
            "model": self.active_model,
            "config": self.providers.get(self.active_provider, {})
        }
    
    async def check_service_health(self, provider_id: str = None) -> Dict[str, Any]:
        """Check health of LLM service"""
        providers_to_check = [provider_id] if provider_id else list(self.providers.keys())
        results = {}
        
        for pid in providers_to_check:
            config = self.providers.get(pid, {})
            
            try:
                if pid == "ollama":
                    result = await self._check_ollama_health(config)
                elif pid == "openai":
                    result = await self._check_openai_health(config)
                elif pid == "anthropic":
                    result = await self._check_anthropic_health(config)
                else:
                    result = {"status": "unknown", "error": "Unknown provider"}
                
                results[pid] = result
                self._service_status[pid] = result
                
            except Exception as e:
                results[pid] = {"status": "error", "error": str(e)}
                self._service_status[pid] = results[pid]
        
        return results
    
    async def _check_ollama_health(self, config: Dict) -> Dict:
        """Check Ollama service health"""
        base_url = config.get("base_url", "http://localhost:11434")
        
        try:
            response = await self.http_client.get(f"{base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                return {
                    "status": "healthy",
                    "available_models": models,
                    "url": base_url
                }
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
        except httpx.ConnectError:
            return {"status": "offline", "error": "Cannot connect to Ollama"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _check_openai_health(self, config: Dict) -> Dict:
        """Check OpenAI API health"""
        api_key = config.get("api_key", "")
        
        if not api_key:
            return {"status": "not_configured", "error": "API key not set"}
        
        try:
            response = await self.http_client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if response.status_code == 200:
                return {"status": "healthy"}
            elif response.status_code == 401:
                return {"status": "error", "error": "Invalid API key"}
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _check_anthropic_health(self, config: Dict) -> Dict:
        """Check Anthropic API health"""
        api_key = config.get("api_key", "")
        
        if not api_key:
            return {"status": "not_configured", "error": "API key not set"}
        
        # Anthropic doesn't have a simple health endpoint, assume healthy if key exists
        return {"status": "configured", "note": "Key configured, ready to use"}
    
    async def get_available_models(self, provider_id: str = None) -> Dict[str, List[str]]:
        """Get available models for provider(s)"""
        providers_to_check = [provider_id] if provider_id else list(self.providers.keys())
        results = {}
        
        for pid in providers_to_check:
            config = self.providers.get(pid, {})
            
            if pid == "ollama":
                health = await self._check_ollama_health(config)
                results[pid] = health.get("available_models", [])
            else:
                # Use configured models for API providers
                results[pid] = config.get("models", [])
        
        return results
    
    async def chat(self, message: str, system_prompt: str = None, 
                   history: List[Dict] = None) -> LLMResponse:
        """Send chat message to active LLM"""
        provider = self.active_provider
        model = self.active_model
        config = self.providers.get(provider, {})
        
        try:
            if provider == "ollama":
                return await self._chat_ollama(message, model, config, system_prompt, history)
            elif provider == "openai":
                return await self._chat_openai(message, model, config, system_prompt, history)
            elif provider == "anthropic":
                return await self._chat_anthropic(message, model, config, system_prompt, history)
            else:
                return LLMResponse(
                    content="",
                    model=model,
                    provider=provider,
                    error=f"Unknown provider: {provider}"
                )
        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            return LLMResponse(
                content="",
                model=model,
                provider=provider,
                error=str(e)
            )
    
    async def _chat_ollama(self, message: str, model: str, config: Dict,
                          system_prompt: str = None, history: List[Dict] = None) -> LLMResponse:
        """Chat with Ollama"""
        base_url = config.get("base_url", "http://localhost:11434")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.http_client.post(
                f"{base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return LLMResponse(
                    content=data.get("message", {}).get("content", ""),
                    model=model,
                    provider="ollama",
                    tokens_used=data.get("eval_count", 0)
                )
            else:
                return LLMResponse(
                    content="",
                    model=model,
                    provider="ollama",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        except httpx.ConnectError:
            return LLMResponse(
                content="",
                model=model,
                provider="ollama",
                error="Cannot connect to Ollama. Is it running?"
            )
    
    async def _chat_openai(self, message: str, model: str, config: Dict,
                          system_prompt: str = None, history: List[Dict] = None) -> LLMResponse:
        """Chat with OpenAI"""
        api_key = config.get("api_key", "")
        
        if not api_key:
            return LLMResponse(content="", model=model, provider="openai", error="API key not configured")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})
        
        response = await self.http_client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": messages,
                "temperature": config.get("temperature", 0.7)
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=model,
                provider="openai",
                tokens_used=data.get("usage", {}).get("total_tokens", 0)
            )
        else:
            return LLMResponse(content="", model=model, provider="openai", error=f"HTTP {response.status_code}")
    
    async def _chat_anthropic(self, message: str, model: str, config: Dict,
                             system_prompt: str = None, history: List[Dict] = None) -> LLMResponse:
        """Chat with Anthropic Claude"""
        api_key = config.get("api_key", "")
        
        if not api_key:
            return LLMResponse(content="", model=model, provider="anthropic", error="API key not configured")
        
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})
        
        response = await self.http_client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "max_tokens": config.get("max_tokens", 2048),
                "system": system_prompt or "",
                "messages": messages
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", [{}])[0].get("text", "")
            return LLMResponse(
                content=content,
                model=model,
                provider="anthropic",
                tokens_used=data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
            )
        else:
            return LLMResponse(content="", model=model, provider="anthropic", error=f"HTTP {response.status_code}")
    
    def get_service_status(self) -> Dict[str, Dict]:
        """Get cached service status"""
        return self._service_status
    
    def get_providers_info(self) -> List[Dict]:
        """Get info about all registered providers"""
        return [
            {
                "id": pid,
                "name": config.get("name", pid),
                "type": config.get("type", pid),
                "is_active": pid == self.active_provider,
                "active_model": self.active_model if pid == self.active_provider else config.get("default_model"),
                "models": config.get("models", []),
                "status": self._service_status.get(pid, {}).get("status", "unknown")
            }
            for pid, config in self.providers.items()
        ]


# Global LLM manager instance
llm_manager = LLMManager()
