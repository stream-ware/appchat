"""
Streamware Registry Manager
Manages internal and external app registries
Allows adding external apps to the system with user access control
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("streamware.registry_manager")

try:
    import tomllib
except ImportError:
    import tomli as tomllib


@dataclass
class ExternalRegistry:
    """External app registry definition"""
    id: str
    name: str
    type: str  # docker, git, npm, pip, http, local
    url: str
    description: str = ""
    enabled: bool = True
    auth_required: bool = False
    auth_config: Dict = field(default_factory=dict)
    apps: List[str] = field(default_factory=list)
    last_sync: Optional[str] = None
    status: str = "unknown"


@dataclass
class ExternalApp:
    """App from external registry"""
    id: str
    name: str
    registry_id: str
    version: str = "latest"
    description: str = ""
    install_cmd: str = ""
    run_cmd: str = ""
    config: Dict = field(default_factory=dict)
    installed: bool = False
    enabled: bool = False
    allowed_users: List[str] = field(default_factory=list)
    allowed_roles: List[str] = field(default_factory=list)


class RegistryManager:
    """
    Manages multiple app registries:
    - Internal (apps/ folder)
    - External (Docker Hub, Git repos, npm, pip, HTTP APIs)
    """
    
    # Supported registry types
    REGISTRY_TYPES = {
        "local": {"name": "Local Apps", "scan_cmd": "ls"},
        "docker": {"name": "Docker Hub", "scan_cmd": "docker search"},
        "git": {"name": "Git Repository", "scan_cmd": "git ls-remote"},
        "npm": {"name": "NPM Registry", "scan_cmd": "npm search"},
        "pip": {"name": "PyPI", "scan_cmd": "pip search"},
        "http": {"name": "HTTP API", "scan_cmd": "curl"},
    }
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.registries_file = self.data_dir / "registries.json"
        self.external_apps_file = self.data_dir / "external_apps.json"
        
        self.registries: Dict[str, ExternalRegistry] = {}
        self.external_apps: Dict[str, ExternalApp] = {}
        
        self._ensure_data_dir()
        self._load_registries()
        self._load_external_apps()
        self._init_default_registries()
        
        logger.info(f"📦 RegistryManager initialized: {len(self.registries)} registries")
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_registries(self):
        """Load registries from file"""
        if self.registries_file.exists():
            try:
                data = json.loads(self.registries_file.read_text())
                for r in data.get("registries", []):
                    self.registries[r["id"]] = ExternalRegistry(**r)
            except Exception as e:
                logger.error(f"Failed to load registries: {e}")
    
    def _load_external_apps(self):
        """Load external apps from file"""
        if self.external_apps_file.exists():
            try:
                data = json.loads(self.external_apps_file.read_text())
                for a in data.get("apps", []):
                    self.external_apps[a["id"]] = ExternalApp(**a)
            except Exception as e:
                logger.error(f"Failed to load external apps: {e}")
    
    def _save_registries(self):
        """Save registries to file"""
        data = {"registries": [vars(r) for r in self.registries.values()]}
        self.registries_file.write_text(json.dumps(data, indent=2, default=str))
    
    def _save_external_apps(self):
        """Save external apps to file"""
        data = {"apps": [vars(a) for a in self.external_apps.values()]}
        self.external_apps_file.write_text(json.dumps(data, indent=2, default=str))
    
    def _init_default_registries(self):
        """Initialize default registries"""
        defaults = [
            ExternalRegistry(
                id="local",
                name="Local Apps",
                type="local",
                url="apps/",
                description="Internal apps in apps/ folder",
                enabled=True
            ),
            ExternalRegistry(
                id="dockerhub",
                name="Docker Hub",
                type="docker",
                url="https://hub.docker.com",
                description="Docker container registry",
                enabled=False
            ),
            ExternalRegistry(
                id="github",
                name="GitHub",
                type="git",
                url="https://github.com",
                description="GitHub repositories",
                enabled=False
            ),
            ExternalRegistry(
                id="ollama",
                name="Ollama Models",
                type="http",
                url="http://localhost:11434",
                description="Local Ollama LLM models",
                enabled=True
            ),
        ]
        
        for reg in defaults:
            if reg.id not in self.registries:
                self.registries[reg.id] = reg
        
        self._save_registries()
    
    # ==================== REGISTRY CRUD ====================
    
    def add_registry(self, registry: Dict) -> bool:
        """Add new external registry"""
        try:
            reg = ExternalRegistry(
                id=registry["id"],
                name=registry["name"],
                type=registry["type"],
                url=registry["url"],
                description=registry.get("description", ""),
                enabled=registry.get("enabled", True),
                auth_required=registry.get("auth_required", False),
                auth_config=registry.get("auth_config", {})
            )
            self.registries[reg.id] = reg
            self._save_registries()
            logger.info(f"✅ Registry added: {reg.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add registry: {e}")
            return False
    
    def remove_registry(self, registry_id: str) -> bool:
        """Remove registry"""
        if registry_id in self.registries:
            del self.registries[registry_id]
            self._save_registries()
            logger.info(f"🗑️ Registry removed: {registry_id}")
            return True
        return False
    
    def update_registry(self, registry_id: str, updates: Dict) -> bool:
        """Update registry settings"""
        if registry_id not in self.registries:
            return False
        
        reg = self.registries[registry_id]
        for key, value in updates.items():
            if hasattr(reg, key):
                setattr(reg, key, value)
        
        self._save_registries()
        logger.info(f"📝 Registry updated: {registry_id}")
        return True
    
    def get_registry(self, registry_id: str) -> Optional[ExternalRegistry]:
        """Get registry by ID"""
        return self.registries.get(registry_id)
    
    def get_all_registries(self) -> List[Dict]:
        """Get all registries"""
        return [
            {
                "id": r.id,
                "name": r.name,
                "type": r.type,
                "url": r.url,
                "description": r.description,
                "enabled": r.enabled,
                "status": r.status,
                "apps_count": len(r.apps),
                "last_sync": r.last_sync
            }
            for r in self.registries.values()
        ]
    
    # ==================== EXTERNAL APPS ====================
    
    def add_external_app(self, app_data: Dict) -> bool:
        """Add external app to system"""
        try:
            app = ExternalApp(
                id=app_data["id"],
                name=app_data["name"],
                registry_id=app_data["registry_id"],
                version=app_data.get("version", "latest"),
                description=app_data.get("description", ""),
                install_cmd=app_data.get("install_cmd", ""),
                run_cmd=app_data.get("run_cmd", ""),
                config=app_data.get("config", {}),
                allowed_roles=app_data.get("allowed_roles", ["admin"])
            )
            self.external_apps[app.id] = app
            self._save_external_apps()
            
            # Update registry apps list
            if app.registry_id in self.registries:
                if app.id not in self.registries[app.registry_id].apps:
                    self.registries[app.registry_id].apps.append(app.id)
                    self._save_registries()
            
            logger.info(f"✅ External app added: {app.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add external app: {e}")
            return False
    
    def remove_external_app(self, app_id: str) -> bool:
        """Remove external app"""
        if app_id in self.external_apps:
            app = self.external_apps[app_id]
            
            # Remove from registry apps list
            if app.registry_id in self.registries:
                if app.id in self.registries[app.registry_id].apps:
                    self.registries[app.registry_id].apps.remove(app.id)
                    self._save_registries()
            
            del self.external_apps[app_id]
            self._save_external_apps()
            logger.info(f"🗑️ External app removed: {app_id}")
            return True
        return False
    
    def install_external_app(self, app_id: str) -> Dict[str, Any]:
        """Install external app"""
        if app_id not in self.external_apps:
            return {"success": False, "error": "App not found"}
        
        app = self.external_apps[app_id]
        
        if not app.install_cmd:
            return {"success": False, "error": "No install command defined"}
        
        try:
            import subprocess
            result = subprocess.run(
                app.install_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                app.installed = True
                self._save_external_apps()
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def grant_access(self, app_id: str, user_or_role: str, is_role: bool = True) -> bool:
        """Grant user/role access to external app"""
        if app_id not in self.external_apps:
            return False
        
        app = self.external_apps[app_id]
        
        if is_role:
            if user_or_role not in app.allowed_roles:
                app.allowed_roles.append(user_or_role)
        else:
            if user_or_role not in app.allowed_users:
                app.allowed_users.append(user_or_role)
        
        self._save_external_apps()
        return True
    
    def revoke_access(self, app_id: str, user_or_role: str, is_role: bool = True) -> bool:
        """Revoke user/role access to external app"""
        if app_id not in self.external_apps:
            return False
        
        app = self.external_apps[app_id]
        
        if is_role:
            if user_or_role in app.allowed_roles:
                app.allowed_roles.remove(user_or_role)
        else:
            if user_or_role in app.allowed_users:
                app.allowed_users.remove(user_or_role)
        
        self._save_external_apps()
        return True
    
    def check_access(self, app_id: str, user: str, role: str) -> bool:
        """Check if user/role has access to app"""
        if app_id not in self.external_apps:
            return False
        
        app = self.external_apps[app_id]
        return user in app.allowed_users or role in app.allowed_roles
    
    def get_external_apps(self, registry_id: str = None) -> List[Dict]:
        """Get external apps, optionally filtered by registry"""
        apps = []
        for app in self.external_apps.values():
            if registry_id and app.registry_id != registry_id:
                continue
            apps.append({
                "id": app.id,
                "name": app.name,
                "registry_id": app.registry_id,
                "version": app.version,
                "description": app.description,
                "installed": app.installed,
                "enabled": app.enabled,
                "allowed_roles": app.allowed_roles
            })
        return apps
    
    # ==================== SYNC ====================
    
    async def sync_registry(self, registry_id: str) -> Dict[str, Any]:
        """Sync apps from external registry"""
        if registry_id not in self.registries:
            return {"success": False, "error": "Registry not found"}
        
        reg = self.registries[registry_id]
        
        try:
            if reg.type == "docker":
                return await self._sync_docker_registry(reg)
            elif reg.type == "ollama":
                return await self._sync_ollama_registry(reg)
            elif reg.type == "local":
                return self._sync_local_registry(reg)
            else:
                return {"success": False, "error": f"Unsupported registry type: {reg.type}"}
        except Exception as e:
            reg.status = "error"
            return {"success": False, "error": str(e)}
    
    def _sync_local_registry(self, reg: ExternalRegistry) -> Dict[str, Any]:
        """Sync local apps folder"""
        apps_dir = Path(__file__).parent.parent / reg.url
        
        if not apps_dir.exists():
            return {"success": False, "error": "Apps directory not found"}
        
        found_apps = []
        for app_path in apps_dir.iterdir():
            if app_path.is_dir() and (app_path / "manifest.toml").exists():
                found_apps.append(app_path.name)
        
        reg.apps = found_apps
        reg.last_sync = datetime.now().isoformat()
        reg.status = "healthy"
        self._save_registries()
        
        return {"success": True, "apps": found_apps}
    
    async def _sync_ollama_registry(self, reg: ExternalRegistry) -> Dict[str, Any]:
        """Sync Ollama models"""
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{reg.url}/api/tags")
                
                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    
                    reg.apps = models
                    reg.last_sync = datetime.now().isoformat()
                    reg.status = "healthy"
                    self._save_registries()
                    
                    return {"success": True, "apps": models}
                else:
                    reg.status = "error"
                    return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            reg.status = "offline"
            return {"success": False, "error": str(e)}
    
    async def _sync_docker_registry(self, reg: ExternalRegistry) -> Dict[str, Any]:
        """Sync Docker registry (placeholder)"""
        # Would need Docker API integration
        reg.status = "not_implemented"
        return {"success": False, "error": "Docker sync not implemented yet"}


# Global registry manager instance
registry_manager = RegistryManager()
