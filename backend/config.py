"""
Streamware Configuration Module
Loads and validates configuration from .env file
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger("streamware.config")

# Load .env file
ENV_FILE = Path(__file__).parent.parent / ".env"

def load_env_file():
    """Load environment variables from .env file"""
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value

# Load on import
load_env_file()


def get_env(key: str, default: Any = None, cast: type = str) -> Any:
    """Get environment variable with type casting"""
    value = os.environ.get(key, default)
    
    if value is None:
        return default
    
    if cast == bool:
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes", "on")
    
    if cast == int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    if cast == float:
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    if cast == list:
        if isinstance(value, list):
            return value
        return [v.strip() for v in str(value).split(",") if v.strip()]
    
    return str(value) if value else default


@dataclass
class ServerConfig:
    host: str = field(default_factory=lambda: get_env("SERVER_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: get_env("SERVER_PORT", 8002, int))
    debug: bool = field(default_factory=lambda: get_env("DEBUG", True, bool))
    log_level: str = field(default_factory=lambda: get_env("LOG_LEVEL", "INFO"))


@dataclass
class DatabaseConfig:
    url: str = field(default_factory=lambda: get_env("DATABASE_URL", "sqlite:///data/streamware.db"))
    echo: bool = field(default_factory=lambda: get_env("DATABASE_ECHO", False, bool))


@dataclass
class SessionConfig:
    timeout_minutes: int = field(default_factory=lambda: get_env("SESSION_TIMEOUT_MINUTES", 60, int))
    max_history: int = field(default_factory=lambda: get_env("MAX_HISTORY_PER_SESSION", 100, int))


@dataclass
class LLMConfig:
    provider: str = field(default_factory=lambda: get_env("LLM_PROVIDER", "ollama"))
    model: str = field(default_factory=lambda: get_env("LLM_MODEL", "llama2"))
    temperature: float = field(default_factory=lambda: get_env("LLM_TEMPERATURE", 0.7, float))
    max_tokens: int = field(default_factory=lambda: get_env("LLM_MAX_TOKENS", 2048, int))
    ollama_url: str = field(default_factory=lambda: get_env("OLLAMA_BASE_URL", "http://localhost:11434"))
    openai_key: str = field(default_factory=lambda: get_env("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: get_env("OPENAI_MODEL", "gpt-3.5-turbo"))
    anthropic_key: str = field(default_factory=lambda: get_env("ANTHROPIC_API_KEY", ""))
    anthropic_model: str = field(default_factory=lambda: get_env("ANTHROPIC_MODEL", "claude-3-haiku-20240307"))


@dataclass
class TTSConfig:
    enabled: bool = field(default_factory=lambda: get_env("TTS_ENABLED", True, bool))
    language: str = field(default_factory=lambda: get_env("TTS_LANGUAGE", "pl-PL"))


@dataclass
class STTConfig:
    enabled: bool = field(default_factory=lambda: get_env("STT_ENABLED", True, bool))
    language: str = field(default_factory=lambda: get_env("STT_LANGUAGE", "pl-PL"))


@dataclass
class IntegrationConfig:
    weather_url: str = field(default_factory=lambda: get_env("WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast"))
    crypto_url: str = field(default_factory=lambda: get_env("CRYPTO_API_URL", "https://api.coingecko.com/api/v3"))
    exchange_url: str = field(default_factory=lambda: get_env("EXCHANGE_API_URL", "https://api.exchangerate.host"))
    news_api_key: str = field(default_factory=lambda: get_env("NEWS_API_KEY", ""))


@dataclass
class MQTTConfig:
    broker: str = field(default_factory=lambda: get_env("MQTT_BROKER", "test.mosquitto.org"))
    port: int = field(default_factory=lambda: get_env("MQTT_PORT", 1883, int))
    username: str = field(default_factory=lambda: get_env("MQTT_USERNAME", ""))
    password: str = field(default_factory=lambda: get_env("MQTT_PASSWORD", ""))


@dataclass
class EmailConfig:
    smtp_host: str = field(default_factory=lambda: get_env("SMTP_HOST", ""))
    smtp_port: int = field(default_factory=lambda: get_env("SMTP_PORT", 587, int))
    smtp_username: str = field(default_factory=lambda: get_env("SMTP_USERNAME", ""))
    smtp_password: str = field(default_factory=lambda: get_env("SMTP_PASSWORD", ""))
    from_email: str = field(default_factory=lambda: get_env("SMTP_FROM_EMAIL", "noreply@streamware.local"))


@dataclass
class SecurityConfig:
    secret_key: str = field(default_factory=lambda: get_env("SECRET_KEY", "change-this-in-production"))
    admin_username: str = field(default_factory=lambda: get_env("ADMIN_USERNAME", "admin"))
    admin_password: str = field(default_factory=lambda: get_env("ADMIN_PASSWORD", "admin123"))
    cors_origins: list = field(default_factory=lambda: get_env("CORS_ORIGINS", "*", list))


@dataclass
class FeatureFlags:
    voice_control: bool = field(default_factory=lambda: get_env("FEATURE_VOICE_CONTROL", True, bool))
    internet_integrations: bool = field(default_factory=lambda: get_env("FEATURE_INTERNET_INTEGRATIONS", True, bool))
    smart_home: bool = field(default_factory=lambda: get_env("FEATURE_SMART_HOME", True, bool))
    analytics: bool = field(default_factory=lambda: get_env("FEATURE_ANALYTICS", True, bool))
    llm_chat: bool = field(default_factory=lambda: get_env("FEATURE_LLM_CHAT", True, bool))


@dataclass
class LoggingConfig:
    to_file: bool = field(default_factory=lambda: get_env("LOG_TO_FILE", True, bool))
    to_yaml: bool = field(default_factory=lambda: get_env("LOG_TO_YAML", True, bool))
    log_dir: str = field(default_factory=lambda: get_env("LOG_DIR", "logs"))
    conversation_log: bool = field(default_factory=lambda: get_env("CONVERSATION_LOG_ENABLED", True, bool))


@dataclass
class RateLimitConfig:
    requests: int = field(default_factory=lambda: get_env("RATE_LIMIT_REQUESTS", 100, int))
    window_seconds: int = field(default_factory=lambda: get_env("RATE_LIMIT_WINDOW_SECONDS", 60, int))


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.server = ServerConfig()
        self.database = DatabaseConfig()
        self.session = SessionConfig()
        self.llm = LLMConfig()
        self.tts = TTSConfig()
        self.stt = STTConfig()
        self.integrations = IntegrationConfig()
        self.mqtt = MQTTConfig()
        self.email = EmailConfig()
        self.security = SecurityConfig()
        self.features = FeatureFlags()
        self.logging = LoggingConfig()
        self.rate_limit = RateLimitConfig()
        
        self._validate()
    
    def _validate(self):
        """Validate configuration"""
        errors = []
        
        if self.server.port < 1 or self.server.port > 65535:
            errors.append(f"Invalid SERVER_PORT: {self.server.port}")
        
        if self.llm.temperature < 0 or self.llm.temperature > 2:
            errors.append(f"Invalid LLM_TEMPERATURE: {self.llm.temperature}")
        
        if self.security.secret_key == "change-this-in-production":
            logger.warning("⚠️ Using default SECRET_KEY - change in production!")
        
        if errors:
            for error in errors:
                logger.error(f"❌ Config error: {error}")
        else:
            logger.info("✅ Configuration validated")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "server": self.server.__dict__,
            "database": self.database.__dict__,
            "session": self.session.__dict__,
            "llm": {**self.llm.__dict__, "openai_key": "***" if self.llm.openai_key else "", "anthropic_key": "***" if self.llm.anthropic_key else ""},
            "tts": self.tts.__dict__,
            "stt": self.stt.__dict__,
            "integrations": self.integrations.__dict__,
            "mqtt": {**self.mqtt.__dict__, "password": "***" if self.mqtt.password else ""},
            "email": {**self.email.__dict__, "smtp_password": "***" if self.email.smtp_password else ""},
            "security": {"cors_origins": self.security.cors_origins},
            "features": self.features.__dict__,
            "logging": self.logging.__dict__,
            "rate_limit": self.rate_limit.__dict__,
        }
    
    def get_env_template(self) -> str:
        """Generate .env template with all variables"""
        return """# ============================================
# STREAMWARE CONFIGURATION
# ============================================

# Server settings
SERVER_HOST={server.host}
SERVER_PORT={server.port}
DEBUG={debug}
LOG_LEVEL={server.log_level}

# Database
DATABASE_URL={database.url}
DATABASE_ECHO={database.echo}

# Session settings
SESSION_TIMEOUT_MINUTES={session.timeout_minutes}
MAX_HISTORY_PER_SESSION={session.max_history}

# LLM Configuration
LLM_PROVIDER={llm.provider}
LLM_MODEL={llm.model}
LLM_TEMPERATURE={llm.temperature}
LLM_MAX_TOKENS={llm.max_tokens}
OLLAMA_BASE_URL={llm.ollama_url}

# TTS/STT Settings
TTS_ENABLED={tts.enabled}
TTS_LANGUAGE={tts.language}
STT_ENABLED={stt.enabled}
STT_LANGUAGE={stt.language}

# Feature Flags
FEATURE_VOICE_CONTROL={features.voice_control}
FEATURE_INTERNET_INTEGRATIONS={features.internet_integrations}
FEATURE_SMART_HOME={features.smart_home}
FEATURE_ANALYTICS={features.analytics}
FEATURE_LLM_CHAT={features.llm_chat}
""".format(
            server=self.server,
            debug=str(self.server.debug).lower(),
            database=self.database,
            session=self.session,
            llm=self.llm,
            tts=self.tts,
            stt=self.stt,
            features=self.features,
        )


# Global config instance
config = Config()


def get_config() -> Config:
    """Get global config instance"""
    return config


def reload_config():
    """Reload configuration from .env"""
    global config
    load_env_file()
    config = Config()
    logger.info("🔄 Configuration reloaded")
    return config
