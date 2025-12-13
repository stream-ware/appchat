"""
Streamware Database Module
SQLite database for conversations, configuration, and system data
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger("streamware.database")

# Ensure data directory exists
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATA_DIR / "streamware.db"


class Database:
    """SQLite database manager for Streamware"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DATABASE_PATH)
        self._init_database()
        logger.info(f"💾 Database initialized: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    type TEXT DEFAULT 'string',
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    command TEXT NOT NULL,
                    response TEXT,
                    app_type TEXT,
                    action TEXT,
                    intent_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'guest',
                    display_name TEXT,
                    permissions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # LLM Providers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS llm_providers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    base_url TEXT,
                    api_key TEXT,
                    models TEXT,
                    default_model TEXT,
                    is_active INTEGER DEFAULT 1,
                    is_default INTEGER DEFAULT 0,
                    config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Services health table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS services (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    url TEXT,
                    status TEXT DEFAULT 'unknown',
                    last_check TIMESTAMP,
                    error_message TEXT,
                    config TEXT
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
            
            # Insert default config if not exists
            self._insert_default_config(cursor)
            self._insert_default_llm_providers(cursor)
            self._insert_default_services(cursor)
    
    def _insert_default_config(self, cursor):
        """Insert default configuration values"""
        defaults = [
            ("llm_provider", "ollama", "string", "Active LLM provider"),
            ("llm_model", "llama2", "string", "Active LLM model"),
            ("llm_temperature", "0.7", "float", "LLM temperature"),
            ("tts_enabled", "true", "bool", "Text-to-speech enabled"),
            ("stt_enabled", "true", "bool", "Speech-to-text enabled"),
            ("theme", "dark", "string", "UI theme"),
            ("language", "pl", "string", "System language"),
            ("max_history", "100", "int", "Max conversation history"),
            ("session_timeout", "60", "int", "Session timeout in minutes"),
            ("ollama_url", "http://localhost:11434", "string", "Ollama API URL"),
        ]
        
        for key, value, type_, desc in defaults:
            cursor.execute("""
                INSERT OR IGNORE INTO config (key, value, type, description)
                VALUES (?, ?, ?, ?)
            """, (key, value, type_, desc))
    
    def _insert_default_llm_providers(self, cursor):
        """Insert default LLM providers"""
        providers = [
            {
                "id": "ollama",
                "name": "Ollama (Local)",
                "type": "ollama",
                "base_url": "http://localhost:11434",
                "models": json.dumps(["llama2", "mistral", "codellama", "llama2-uncensored"]),
                "default_model": "llama2",
                "is_active": 1,
                "is_default": 1
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "type": "openai",
                "base_url": "https://api.openai.com/v1",
                "models": json.dumps(["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]),
                "default_model": "gpt-3.5-turbo",
                "is_active": 0,
                "is_default": 0
            },
            {
                "id": "anthropic",
                "name": "Anthropic Claude",
                "type": "anthropic",
                "base_url": "https://api.anthropic.com",
                "models": json.dumps(["claude-3-haiku-20240307", "claude-3-sonnet-20240229"]),
                "default_model": "claude-3-haiku-20240307",
                "is_active": 0,
                "is_default": 0
            }
        ]
        
        for p in providers:
            cursor.execute("""
                INSERT OR IGNORE INTO llm_providers (id, name, type, base_url, models, default_model, is_active, is_default)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (p["id"], p["name"], p["type"], p["base_url"], p["models"], p["default_model"], p["is_active"], p["is_default"]))
    
    def _insert_default_services(self, cursor):
        """Insert default services"""
        services = [
            ("ollama", "Ollama LLM", "llm", "http://localhost:11434"),
            ("weather", "Weather API", "api", "https://api.open-meteo.com"),
            ("crypto", "CoinGecko API", "api", "https://api.coingecko.com"),
            ("mqtt", "MQTT Broker", "mqtt", "test.mosquitto.org:1883"),
        ]
        
        for sid, name, stype, url in services:
            cursor.execute("""
                INSERT OR IGNORE INTO services (id, name, type, url, status)
                VALUES (?, ?, ?, ?, 'unknown')
            """, (sid, name, stype, url))
    
    # ==================== CONFIG ====================
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value, type FROM config WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            if not row:
                return default
            
            value, type_ = row["value"], row["type"]
            
            # Convert to appropriate type
            if type_ == "int":
                return int(value)
            elif type_ == "float":
                return float(value)
            elif type_ == "bool":
                return value.lower() in ("true", "1", "yes")
            elif type_ == "json":
                return json.loads(value)
            return value
    
    def set_config(self, key: str, value: Any, type_: str = "string", description: str = None):
        """Set configuration value"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
            type_ = "json"
        elif isinstance(value, bool):
            value = "true" if value else "false"
            type_ = "bool"
        else:
            value = str(value)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO config (key, value, type, description, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    type = excluded.type,
                    description = COALESCE(excluded.description, config.description),
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value, type_, description))
        
        logger.info(f"⚙️ Config updated: {key} = {value}")
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration values"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value, type, description FROM config")
            
            config = {}
            for row in cursor.fetchall():
                key, value, type_, desc = row["key"], row["value"], row["type"], row["description"]
                
                if type_ == "int":
                    value = int(value)
                elif type_ == "float":
                    value = float(value)
                elif type_ == "bool":
                    value = value.lower() in ("true", "1", "yes")
                elif type_ == "json":
                    value = json.loads(value)
                
                config[key] = {"value": value, "type": type_, "description": desc}
            
            return config
    
    # ==================== CONVERSATIONS ====================
    
    def save_conversation(self, session_id: str, command: str, response: str,
                         app_type: str = None, action: str = None,
                         intent_data: Dict = None, user_id: str = None):
        """Save conversation entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (session_id, user_id, command, response, app_type, action, intent_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, command, response, app_type, action,
                  json.dumps(intent_data) if intent_data else None))
            
            # Update session last activity
            cursor.execute("""
                UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE id = ?
            """, (session_id,))
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT command, response, app_type, action, created_at
                FROM conversations
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (session_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_conversations(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all conversations (admin)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, s.user_id as session_user
                FROM conversations c
                LEFT JOIN sessions s ON c.session_id = s.id
                ORDER BY c.created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== SESSIONS ====================
    
    def create_session(self, session_id: str, user_id: str = None, metadata: Dict = None):
        """Create new session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sessions (id, user_id, metadata, started_at, last_activity)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (session_id, user_id, json.dumps(metadata) if metadata else None))
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_active_sessions(self) -> List[Dict]:
        """Get all active sessions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions
                WHERE last_activity > datetime('now', '-1 hour')
                ORDER BY last_activity DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== LLM PROVIDERS ====================
    
    def get_llm_providers(self) -> List[Dict]:
        """Get all LLM providers"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM llm_providers ORDER BY is_default DESC, name")
            
            providers = []
            for row in cursor.fetchall():
                p = dict(row)
                p["models"] = json.loads(p["models"]) if p["models"] else []
                p["config"] = json.loads(p["config"]) if p["config"] else {}
                providers.append(p)
            
            return providers
    
    def get_active_llm(self) -> Optional[Dict]:
        """Get active LLM provider"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM llm_providers WHERE is_default = 1 AND is_active = 1")
            row = cursor.fetchone()
            
            if row:
                p = dict(row)
                p["models"] = json.loads(p["models"]) if p["models"] else []
                p["config"] = json.loads(p["config"]) if p["config"] else {}
                return p
            return None
    
    def set_active_llm(self, provider_id: str, model: str = None):
        """Set active LLM provider"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Reset all defaults
            cursor.execute("UPDATE llm_providers SET is_default = 0")
            
            # Set new default
            cursor.execute("UPDATE llm_providers SET is_default = 1 WHERE id = ?", (provider_id,))
            
            if model:
                cursor.execute("UPDATE llm_providers SET default_model = ? WHERE id = ?", (model, provider_id))
            
            # Update config
            cursor.execute("UPDATE config SET value = ? WHERE key = 'llm_provider'", (provider_id,))
            if model:
                cursor.execute("UPDATE config SET value = ? WHERE key = 'llm_model'", (model,))
        
        logger.info(f"🤖 Active LLM changed to: {provider_id}/{model}")
    
    def update_llm_provider(self, provider_id: str, **kwargs):
        """Update LLM provider settings"""
        allowed_fields = ["name", "base_url", "api_key", "models", "default_model", "is_active", "config"]
        
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                if field in ("models", "config") and isinstance(value, (dict, list)):
                    value = json.dumps(value)
                updates.append(f"{field} = ?")
                values.append(value)
        
        if updates:
            values.append(provider_id)
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE llm_providers SET {', '.join(updates)} WHERE id = ?", values)
    
    # ==================== SERVICES ====================
    
    def get_services(self) -> List[Dict]:
        """Get all services"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM services ORDER BY name")
            
            services = []
            for row in cursor.fetchall():
                s = dict(row)
                s["config"] = json.loads(s["config"]) if s["config"] else {}
                services.append(s)
            
            return services
    
    def update_service_status(self, service_id: str, status: str, error_message: str = None):
        """Update service status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE services SET status = ?, error_message = ?, last_check = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, error_message, service_id))
    
    def get_service(self, service_id: str) -> Optional[Dict]:
        """Get service by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
            row = cursor.fetchone()
            if row:
                s = dict(row)
                s["config"] = json.loads(s["config"]) if s["config"] else {}
                return s
            return None


# Global database instance
db = Database()
