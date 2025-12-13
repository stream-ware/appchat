#!/usr/bin/env python3
"""
CurlLM Client - Universal LLM interface
Uses curllm library for multi-provider LLM access
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Try to import curllm, provide fallback
try:
    import curllm
    HAS_CURLLM = True
except ImportError:
    HAS_CURLLM = False

# Add services to path
sys.path.insert(0, str(APP_DIR.parent.parent))


class CurlLMClient:
    """
    Universal LLM client supporting multiple providers
    Providers: Ollama, OpenAI, Anthropic, etc.
    """
    
    def __init__(self):
        self.config_file = DATA_DIR / "config.json"
        self.history_file = DATA_DIR / "history.json"
        self.config = self._load_config()
        self.history: List[Dict] = self._load_history()
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return json.load(f)
        
        # Default config
        return {
            "provider": os.getenv("LLM_PROVIDER", "ollama"),
            "model": os.getenv("LLM_MODEL", "llama2"),
            "ollama_url": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            "openai_key": os.getenv("OPENAI_API_KEY", ""),
            "anthropic_key": os.getenv("ANTHROPIC_API_KEY", ""),
            "temperature": 0.7,
            "max_tokens": 2048,
            "system_prompt": "Jesteś pomocnym asystentem. Odpowiadaj zwięźle i konkretnie."
        }
    
    def _save_config(self):
        """Save configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def _load_history(self) -> List[Dict]:
        """Load chat history"""
        if self.history_file.exists():
            with open(self.history_file, "r") as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save chat history"""
        # Keep last 100 messages
        with open(self.history_file, "w") as f:
            json.dump(self.history[-100:], f, indent=2)
    
    def query(self, prompt: str, system_prompt: str = None, context: List[Dict] = None) -> Dict[str, Any]:
        """
        Send query to LLM
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt override
            context: Optional conversation context
        
        Returns:
            {"success": bool, "response": str, "model": str, "tokens": int}
        """
        if not HAS_CURLLM:
            return self._fallback_query(prompt, system_prompt, context)
        
        try:
            # Build messages
            messages = []
            
            # System prompt
            sys_prompt = system_prompt or self.config.get("system_prompt", "")
            if sys_prompt:
                messages.append({"role": "system", "content": sys_prompt})
            
            # Context from previous messages
            if context:
                messages.extend(context)
            
            # Current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Use curllm
            provider = self.config.get("provider", "ollama")
            model = self.config.get("model", "llama2")
            
            if provider == "ollama":
                response = curllm.chat(
                    model=model,
                    messages=messages,
                    base_url=self.config.get("ollama_url"),
                    temperature=self.config.get("temperature", 0.7)
                )
            elif provider == "openai":
                response = curllm.chat(
                    model=model,
                    messages=messages,
                    api_key=self.config.get("openai_key"),
                    temperature=self.config.get("temperature", 0.7)
                )
            elif provider == "anthropic":
                response = curllm.chat(
                    model=model,
                    messages=messages,
                    api_key=self.config.get("anthropic_key"),
                    temperature=self.config.get("temperature", 0.7)
                )
            else:
                return {"success": False, "error": f"Unknown provider: {provider}"}
            
            # Save to history
            self.history.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now().isoformat()
            })
            self.history.append({
                "role": "assistant",
                "content": response.content,
                "model": f"{provider}/{model}",
                "timestamp": datetime.now().isoformat()
            })
            self._save_history()
            
            return {
                "success": True,
                "response": response.content,
                "model": f"{provider}/{model}",
                "tokens": getattr(response, "usage", {}).get("total_tokens", 0)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _fallback_query(self, prompt: str, system_prompt: str = None, context: List[Dict] = None) -> Dict:
        """Fallback query using httpx when curllm not available"""
        import httpx
        
        provider = self.config.get("provider", "ollama")
        model = self.config.get("model", "llama2")
        
        try:
            if provider == "ollama":
                url = f"{self.config.get('ollama_url', 'http://localhost:11434')}/api/chat"
                
                messages = []
                if system_prompt or self.config.get("system_prompt"):
                    messages.append({
                        "role": "system",
                        "content": system_prompt or self.config.get("system_prompt", "")
                    })
                if context:
                    messages.extend(context)
                messages.append({"role": "user", "content": prompt})
                
                with httpx.Client(timeout=60) as client:
                    response = client.post(url, json={
                        "model": model,
                        "messages": messages,
                        "stream": False
                    })
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data.get("message", {}).get("content", "")
                        
                        # Save to history
                        self.history.append({
                            "role": "user",
                            "content": prompt,
                            "timestamp": datetime.now().isoformat()
                        })
                        self.history.append({
                            "role": "assistant",
                            "content": content,
                            "model": f"{provider}/{model}",
                            "timestamp": datetime.now().isoformat()
                        })
                        self._save_history()
                        
                        return {
                            "success": True,
                            "response": content,
                            "model": f"{provider}/{model}",
                            "tokens": data.get("eval_count", 0)
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status_code}"}
            else:
                return {
                    "success": False,
                    "error": f"Provider {provider} requires curllm library. Install with: pip install curllm"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_models(self) -> Dict[str, Any]:
        """List available models"""
        provider = self.config.get("provider", "ollama")
        
        try:
            if provider == "ollama":
                import httpx
                url = f"{self.config.get('ollama_url', 'http://localhost:11434')}/api/tags"
                
                with httpx.Client(timeout=10) as client:
                    response = client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        models = [m["name"] for m in data.get("models", [])]
                        return {
                            "success": True,
                            "provider": provider,
                            "models": models,
                            "current": self.config.get("model")
                        }
            
            # Fallback: return configured models
            return {
                "success": True,
                "provider": provider,
                "models": self._get_provider_models(provider),
                "current": self.config.get("model")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_provider_models(self, provider: str) -> List[str]:
        """Get known models for provider"""
        models = {
            "ollama": ["llama2", "mistral", "codellama", "llama3", "phi"],
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
        }
        return models.get(provider, [])
    
    def set_model(self, model: str, provider: str = None) -> Dict[str, Any]:
        """Set active model"""
        if provider:
            self.config["provider"] = provider
        self.config["model"] = model
        self._save_config()
        
        return {
            "success": True,
            "provider": self.config["provider"],
            "model": model,
            "message": f"Model zmieniony na {self.config['provider']}/{model}"
        }
    
    def get_history(self, limit: int = 20) -> Dict[str, Any]:
        """Get chat history"""
        return {
            "success": True,
            "history": self.history[-limit:],
            "total": len(self.history)
        }
    
    def clear_history(self) -> Dict[str, Any]:
        """Clear chat history"""
        self.history = []
        self._save_history()
        return {"success": True, "message": "Historia wyczyszczona"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get LLM status"""
        provider = self.config.get("provider", "ollama")
        model = self.config.get("model", "llama2")
        
        # Check if provider is available
        available = False
        if provider == "ollama":
            try:
                import httpx
                with httpx.Client(timeout=5) as client:
                    response = client.get(f"{self.config.get('ollama_url')}/api/tags")
                    available = response.status_code == 200
            except:
                pass
        
        return {
            "success": True,
            "provider": provider,
            "model": model,
            "available": available,
            "curllm_installed": HAS_CURLLM,
            "history_count": len(self.history),
            "config": {
                "temperature": self.config.get("temperature"),
                "max_tokens": self.config.get("max_tokens")
            }
        }
    
    # Convenience methods
    def translate(self, text: str, target_lang: str = "en") -> Dict[str, Any]:
        """Translate text"""
        prompt = f"Przetłumacz poniższy tekst na język {target_lang}. Zwróć tylko tłumaczenie:\n\n{text}"
        return self.query(prompt)
    
    def summarize(self, text: str) -> Dict[str, Any]:
        """Summarize text"""
        prompt = f"Podsumuj poniższy tekst w 2-3 zdaniach:\n\n{text}"
        return self.query(prompt)
    
    def explain(self, topic: str) -> Dict[str, Any]:
        """Explain topic"""
        prompt = f"Wyjaśnij prostym językiem: {topic}"
        return self.query(prompt)
    
    def generate_code(self, description: str, language: str = "python") -> Dict[str, Any]:
        """Generate code"""
        prompt = f"Napisz kod w {language} który: {description}\n\nZwróć tylko kod bez wyjaśnień."
        return self.query(prompt)


# Singleton instance
curllm_client = CurlLMClient()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        result = curllm_client.get_status()
    else:
        action = sys.argv[1]
        
        if action == "query" and len(sys.argv) > 2:
            prompt = " ".join(sys.argv[2:])
            result = curllm_client.query(prompt)
        elif action == "models":
            result = curllm_client.list_models()
        elif action == "set-model" and len(sys.argv) > 2:
            result = curllm_client.set_model(sys.argv[2])
        elif action == "history":
            result = curllm_client.get_history()
        elif action == "clear":
            result = curllm_client.clear_history()
        elif action == "status":
            result = curllm_client.get_status()
        elif action == "translate" and len(sys.argv) > 2:
            result = curllm_client.translate(" ".join(sys.argv[2:]))
        elif action == "summarize" and len(sys.argv) > 2:
            result = curllm_client.summarize(" ".join(sys.argv[2:]))
        elif action == "explain" and len(sys.argv) > 2:
            result = curllm_client.explain(" ".join(sys.argv[2:]))
        elif action == "code" and len(sys.argv) > 2:
            result = curllm_client.generate_code(" ".join(sys.argv[2:]))
        else:
            result = {"error": f"Unknown action: {action}"}
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
