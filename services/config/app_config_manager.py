"""
App Configuration Manager
Manages user configuration data for apps with persistence
Allows apps to store and retrieve connection settings, credentials, etc.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
import os

logger = logging.getLogger("streamware.app_config")


@dataclass
class AppConfig:
    """Configuration for a single app"""
    app_id: str
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    credentials: Dict[str, str] = field(default_factory=dict)
    connections: Dict[str, Dict] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class AppConfigManager:
    """
    Manages configuration for all apps
    Stores user settings, credentials, and connection info
    Persists data to disk for restart survival
    """
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent.parent / "data" / "app_configs"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.configs: Dict[str, AppConfig] = {}
        self._load_all_configs()
        logger.info(f"⚙️ AppConfigManager initialized with {len(self.configs)} app configs")
    
    def _load_all_configs(self):
        """Load all app configurations from disk"""
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, "r") as f:
                    data = json.load(f)
                    app_id = data.get("app_id", config_file.stem)
                    self.configs[app_id] = AppConfig(**data)
            except Exception as e:
                logger.warning(f"Failed to load config {config_file}: {e}")
    
    def get_config(self, app_id: str) -> AppConfig:
        """Get configuration for an app, create if not exists"""
        if app_id not in self.configs:
            self.configs[app_id] = AppConfig(app_id=app_id)
        return self.configs[app_id]
    
    def save_config(self, app_id: str):
        """Save app configuration to disk"""
        if app_id not in self.configs:
            return
        
        config = self.configs[app_id]
        config.last_updated = datetime.now().isoformat()
        
        config_file = self.config_dir / f"{app_id}.json"
        with open(config_file, "w") as f:
            json.dump(asdict(config), f, indent=2)
        
        logger.debug(f"Saved config for {app_id}")
    
    def set_setting(self, app_id: str, key: str, value: Any) -> bool:
        """Set a setting for an app"""
        config = self.get_config(app_id)
        config.settings[key] = value
        self.save_config(app_id)
        return True
    
    def get_setting(self, app_id: str, key: str, default: Any = None) -> Any:
        """Get a setting for an app"""
        config = self.get_config(app_id)
        return config.settings.get(key, default)
    
    def set_credential(self, app_id: str, key: str, value: str) -> bool:
        """Set a credential (API key, password, etc.) for an app"""
        config = self.get_config(app_id)
        # In production, these should be encrypted
        config.credentials[key] = value
        self.save_config(app_id)
        logger.info(f"Credential '{key}' set for {app_id}")
        return True
    
    def get_credential(self, app_id: str, key: str) -> Optional[str]:
        """Get a credential for an app"""
        config = self.get_config(app_id)
        return config.credentials.get(key)
    
    def add_connection(self, app_id: str, connection_id: str, connection_data: Dict) -> bool:
        """Add a connection configuration for an app"""
        config = self.get_config(app_id)
        config.connections[connection_id] = {
            **connection_data,
            "added_at": datetime.now().isoformat(),
            "status": "configured"
        }
        self.save_config(app_id)
        logger.info(f"Connection '{connection_id}' added for {app_id}")
        return True
    
    def get_connection(self, app_id: str, connection_id: str) -> Optional[Dict]:
        """Get a connection configuration"""
        config = self.get_config(app_id)
        return config.connections.get(connection_id)
    
    def get_connections(self, app_id: str) -> Dict[str, Dict]:
        """Get all connections for an app"""
        config = self.get_config(app_id)
        return config.connections
    
    def remove_connection(self, app_id: str, connection_id: str) -> bool:
        """Remove a connection"""
        config = self.get_config(app_id)
        if connection_id in config.connections:
            del config.connections[connection_id]
            self.save_config(app_id)
            return True
        return False
    
    def is_configured(self, app_id: str) -> bool:
        """Check if an app has any configuration"""
        config = self.get_config(app_id)
        return bool(config.settings or config.credentials or config.connections)
    
    def get_all_configs(self) -> Dict[str, AppConfig]:
        """Get all app configurations"""
        return self.configs
    
    def export_config(self, app_id: str) -> Dict:
        """Export app config (without credentials)"""
        config = self.get_config(app_id)
        data = asdict(config)
        # Remove sensitive data
        data["credentials"] = {k: "***" for k in data.get("credentials", {})}
        return data


# Singleton instance
app_config_manager = AppConfigManager()
