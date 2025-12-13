"""
Data Loader - Load configuration and data from external JSON/SQLite files
Minimizes hardcoded data in the codebase
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("streamware.data")

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
APPS_DIR = BASE_DIR / "apps"


class DataLoader:
    """Centralized data loading from JSON/SQLite sources"""
    
    _cache: Dict[str, Any] = {}
    
    @classmethod
    def load_json(cls, file_path: Path, cache_key: str = None) -> Dict:
        """Load JSON file with optional caching"""
        if cache_key and cache_key in cls._cache:
            return cls._cache[cache_key]
        
        if not file_path.exists():
            logger.warning(f"Data file not found: {file_path}")
            return {}
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if cache_key:
                cls._cache[cache_key] = data
            
            return data
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return {}
    
    @classmethod
    def save_json(cls, file_path: Path, data: Dict, cache_key: str = None):
        """Save data to JSON file"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if cache_key:
                cls._cache[cache_key] = data
                
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
    
    @classmethod
    def clear_cache(cls, cache_key: str = None):
        """Clear cached data"""
        if cache_key:
            cls._cache.pop(cache_key, None)
        else:
            cls._cache.clear()
    
    @classmethod
    def get_apps_config(cls) -> Dict:
        """Load apps configuration from data/apps_config.json"""
        return cls.load_json(DATA_DIR / "apps_config.json", "apps_config")
    
    @classmethod
    def get_apps(cls) -> Dict:
        """Get apps registry data"""
        config = cls.get_apps_config()
        return config.get("apps", {})
    
    @classmethod
    def get_intents(cls) -> Dict:
        """Get intents mapping (command -> action)"""
        config = cls.get_apps_config()
        intents = {}
        for app_type, commands in config.get("intents", {}).items():
            for cmd, action in commands.items():
                intents[cmd] = (app_type, action)
        return intents
    
    @classmethod
    def get_keywords(cls) -> Dict:
        """Get keywords for fuzzy matching"""
        config = cls.get_apps_config()
        return config.get("keywords", {})
    
    @classmethod
    def get_app_data(cls, app_id: str, filename: str = "data.json") -> Dict:
        """Load app-specific data file"""
        app_data_path = APPS_DIR / app_id / "data" / filename
        return cls.load_json(app_data_path, f"app_{app_id}_{filename}")
    
    @classmethod
    def save_app_data(cls, app_id: str, data: Dict, filename: str = "data.json"):
        """Save app-specific data file"""
        app_data_path = APPS_DIR / app_id / "data" / filename
        cls.save_json(app_data_path, data, f"app_{app_id}_{filename}")


class AppDatabase:
    """SQLite database for app-specific persistent data"""
    
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.db_path = APPS_DIR / app_id / "data" / "app.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_conn(self):
        return sqlite3.connect(self.db_path)
    
    def execute(self, query: str, params: tuple = ()) -> list:
        """Execute SQL query and return results"""
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute write query and return last row id"""
        with self._get_conn() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def init_table(self, table_name: str, schema: str):
        """Create table if not exists"""
        self.execute_write(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
    
    def insert(self, table: str, data: Dict) -> int:
        """Insert row into table"""
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        return self.execute_write(query, tuple(data.values()))
    
    def select(self, table: str, where: str = None, params: tuple = ()) -> list:
        """Select rows from table"""
        query = f"SELECT * FROM {table}"
        if where:
            query += f" WHERE {where}"
        return self.execute(query, params)


# Singleton instances
data_loader = DataLoader()
