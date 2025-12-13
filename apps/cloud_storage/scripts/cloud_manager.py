#!/usr/bin/env python3
"""
Cloud Storage Manager - Connect and manage cloud storage services
Supports: OneDrive, Nextcloud, Google Drive
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
CONFIG_FILE = DATA_DIR / "cloud_config.json"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict:
    """Load cloud storage configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"providers": {}, "sync_folders": [], "last_sync": None}


def save_config(config: Dict):
    """Save cloud storage configuration"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2, default=str)


def connect_provider(provider: str, **kwargs) -> Dict[str, Any]:
    """
    Connect to a cloud storage provider
    
    Supported providers:
    - onedrive: Microsoft OneDrive (requires app registration)
    - nextcloud: Nextcloud/ownCloud (requires server URL + credentials)
    - gdrive: Google Drive (requires OAuth)
    """
    config = load_config()
    
    provider_configs = {
        "onedrive": {
            "name": "Microsoft OneDrive",
            "auth_type": "oauth2",
            "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            "api_url": "https://graph.microsoft.com/v1.0/me/drive",
            "scopes": ["Files.ReadWrite", "offline_access"],
            "setup_instructions": """
Aby połączyć OneDrive:
1. Przejdź do Azure Portal i zarejestruj aplikację
2. Ustaw ONEDRIVE_CLIENT_ID i ONEDRIVE_CLIENT_SECRET w .env
3. Uruchom: make -f Makefile.admin setup-onedrive
"""
        },
        "nextcloud": {
            "name": "Nextcloud",
            "auth_type": "basic",
            "required_params": ["server_url", "username", "password"],
            "setup_instructions": """
Aby połączyć Nextcloud:
1. Ustaw NEXTCLOUD_URL w .env (np. https://cloud.example.com)
2. Ustaw NEXTCLOUD_USER i NEXTCLOUD_PASSWORD
3. Uruchom: make -f Makefile.admin setup-nextcloud
"""
        },
        "gdrive": {
            "name": "Google Drive",
            "auth_type": "oauth2",
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "api_url": "https://www.googleapis.com/drive/v3",
            "scopes": ["https://www.googleapis.com/auth/drive"],
            "setup_instructions": """
Aby połączyć Google Drive:
1. Utwórz projekt w Google Cloud Console
2. Włącz Google Drive API
3. Ustaw GDRIVE_CLIENT_ID i GDRIVE_CLIENT_SECRET w .env
4. Uruchom: make -f Makefile.admin setup-gdrive
"""
        }
    }
    
    if provider not in provider_configs:
        return {
            "success": False,
            "error": f"Unknown provider: {provider}",
            "available": list(provider_configs.keys())
        }
    
    provider_info = provider_configs[provider]
    
    # Check if already connected
    if provider in config.get("providers", {}):
        existing = config["providers"][provider]
        return {
            "success": True,
            "status": "already_connected",
            "provider": provider,
            "name": provider_info["name"],
            "connected_at": existing.get("connected_at")
        }
    
    # Check for required environment variables
    env_vars = {
        "onedrive": ["ONEDRIVE_CLIENT_ID", "ONEDRIVE_CLIENT_SECRET"],
        "nextcloud": ["NEXTCLOUD_URL", "NEXTCLOUD_USER", "NEXTCLOUD_PASSWORD"],
        "gdrive": ["GDRIVE_CLIENT_ID", "GDRIVE_CLIENT_SECRET"]
    }
    
    missing_vars = [v for v in env_vars.get(provider, []) if not os.getenv(v)]
    
    if missing_vars:
        return {
            "success": False,
            "status": "config_required",
            "provider": provider,
            "name": provider_info["name"],
            "missing_env_vars": missing_vars,
            "instructions": provider_info["setup_instructions"]
        }
    
    # Register provider (actual OAuth flow would happen here)
    config["providers"][provider] = {
        "name": provider_info["name"],
        "auth_type": provider_info["auth_type"],
        "connected_at": datetime.now().isoformat(),
        "status": "pending_auth"
    }
    save_config(config)
    
    return {
        "success": True,
        "status": "pending_auth",
        "provider": provider,
        "name": provider_info["name"],
        "message": f"Provider {provider_info['name']} zarejestrowany. Wymagana autoryzacja.",
        "instructions": provider_info["setup_instructions"]
    }


def list_providers() -> Dict[str, Any]:
    """List all configured cloud storage providers"""
    config = load_config()
    providers = config.get("providers", {})
    
    return {
        "success": True,
        "count": len(providers),
        "providers": [
            {
                "id": pid,
                "name": pdata.get("name"),
                "status": pdata.get("status", "unknown"),
                "connected_at": pdata.get("connected_at")
            }
            for pid, pdata in providers.items()
        ]
    }


def get_status() -> Dict[str, Any]:
    """Get overall cloud storage status"""
    config = load_config()
    
    return {
        "success": True,
        "providers_count": len(config.get("providers", {})),
        "sync_folders_count": len(config.get("sync_folders", [])),
        "last_sync": config.get("last_sync"),
        "providers": list(config.get("providers", {}).keys())
    }


def add_sync_folder(local_path: str, remote_path: str, provider: str) -> Dict[str, Any]:
    """Add a folder to sync with cloud storage"""
    config = load_config()
    
    if provider not in config.get("providers", {}):
        return {
            "success": False,
            "error": f"Provider {provider} not connected"
        }
    
    sync_folder = {
        "local_path": local_path,
        "remote_path": remote_path,
        "provider": provider,
        "created_at": datetime.now().isoformat(),
        "last_sync": None
    }
    
    config.setdefault("sync_folders", []).append(sync_folder)
    save_config(config)
    
    return {
        "success": True,
        "message": f"Folder {local_path} dodany do synchronizacji z {provider}:{remote_path}"
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps(get_status(), indent=2))
    else:
        action = sys.argv[1]
        
        if action == "connect":
            provider = sys.argv[2] if len(sys.argv) > 2 else "onedrive"
            result = connect_provider(provider)
        elif action == "list":
            result = list_providers()
        elif action == "status":
            result = get_status()
        else:
            result = {"error": f"Unknown action: {action}"}
        
        print(json.dumps(result, indent=2, default=str))
