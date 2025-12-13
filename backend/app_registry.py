"""
Streamware App Registry
Scans apps/ folder and loads modular apps with manifest.toml
Enables LLM to execute scripts and edit code
Each app has isolated logging in its own logs/ folder
"""

import os
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger("streamware.registry")

try:
    import tomllib
except ImportError:
    import tomli as tomllib

APPS_DIR = Path(__file__).parent.parent / "apps"


class AppLogger:
    """Per-app isolated logger with YAML format"""
    
    def __init__(self, app_id: str, app_path: Path):
        self.app_id = app_id
        self.app_path = app_path
        self.logs_dir = app_path / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create app-specific logger
        self.logger = logging.getLogger(f"app.{app_id}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False  # Don't propagate to root
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # File handler - app.log
        log_file = self.logs_dir / "app.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(file_handler)
        
        # YAML handler - app.yaml
        yaml_file = self.logs_dir / "app.yaml"
        yaml_handler = logging.FileHandler(yaml_file, encoding='utf-8')
        yaml_handler.setFormatter(AppYAMLFormatter(app_id))
        self.logger.addHandler(yaml_handler)
        
        # Errors file - errors.log
        error_file = self.logs_dir / "errors.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        self.logger.addHandler(error_handler)
    
    def info(self, message: str, **extra):
        self.logger.info(message, extra=extra)
    
    def debug(self, message: str, **extra):
        self.logger.debug(message, extra=extra)
    
    def warning(self, message: str, **extra):
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, **extra):
        self.logger.error(message, extra=extra)
    
    def log_command(self, command: str, result: Any):
        """Log command execution"""
        self.logger.info(f"CMD: {command}", extra={
            'type': 'command',
            'command': command,
            'success': result.get('success', False) if isinstance(result, dict) else True
        })
    
    def log_error(self, error_type: str, message: str, details: str = None):
        """Log error with context"""
        self.logger.error(f"{error_type}: {message}", extra={
            'type': 'error',
            'error_type': error_type,
            'details': details
        })
    
    def log_script(self, script_name: str, duration_ms: int, success: bool, output: str = None):
        """Log script execution"""
        self.logger.info(f"SCRIPT: {script_name} ({duration_ms}ms)", extra={
            'type': 'script',
            'script': script_name,
            'duration_ms': duration_ms,
            'success': success
        })
    
    def get_recent_logs(self, lines: int = 50) -> List[str]:
        """Get recent log entries"""
        log_file = self.logs_dir / "app.log"
        if not log_file.exists():
            return []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
    
    def get_recent_errors(self, lines: int = 20) -> List[str]:
        """Get recent error entries"""
        error_file = self.logs_dir / "errors.log"
        if not error_file.exists():
            return []
        
        with open(error_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
    
    def get_yaml_logs(self) -> str:
        """Get YAML formatted logs for LLM context"""
        yaml_file = self.logs_dir / "app.yaml"
        if not yaml_file.exists():
            return ""
        return yaml_file.read_text()


class AppYAMLFormatter(logging.Formatter):
    """YAML formatter for per-app logs"""
    
    def __init__(self, app_id: str):
        super().__init__()
        self.app_id = app_id
    
    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        lines = [f"- {timestamp}:"]
        lines.append(f"    app: {self.app_id}")
        lines.append(f"    level: {record.levelname}")
        lines.append(f"    message: \"{record.getMessage()}\"")
        
        # Add extra fields
        if hasattr(record, 'type'):
            lines.append(f"    type: {record.type}")
        if hasattr(record, 'command'):
            lines.append(f"    command: \"{record.command}\"")
        if hasattr(record, 'script'):
            lines.append(f"    script: {record.script}")
        if hasattr(record, 'duration_ms'):
            lines.append(f"    duration_ms: {record.duration_ms}")
        if hasattr(record, 'success'):
            lines.append(f"    success: {str(record.success).lower()}")
        if hasattr(record, 'error_type'):
            lines.append(f"    error_type: {record.error_type}")
        if hasattr(record, 'details') and record.details:
            lines.append(f"    details: \"{record.details}\"")
        
        return '\n'.join(lines)


@dataclass
class AppManifest:
    """Parsed app manifest"""
    id: str
    name: str
    version: str
    description: str
    language: str
    commands: Dict[str, List[str]]
    keywords: List[str]
    scripts: Dict[str, str]
    error_handling: Dict[str, str]
    service: Dict[str, Any]
    ui: Dict[str, Any]
    path: Path
    enabled: bool = True
    status: str = "unknown"
    last_error: Optional[str] = None
    app_logger: Optional[AppLogger] = None


class AppRegistry:
    """
    Registry for modular apps loaded from apps/ folder
    Each app has: manifest.toml, .env, Makefile, README, scripts/
    """
    
    def __init__(self, apps_dir: Path = None):
        self.apps_dir = apps_dir or APPS_DIR
        self.apps: Dict[str, AppManifest] = {}
        self._command_map: Dict[str, str] = {}  # command -> app_id
        self._keyword_map: Dict[str, str] = {}  # keyword -> app_id
        
        logger.info(f"📦 AppRegistry initialized: {self.apps_dir}")
    
    def scan_apps(self) -> List[str]:
        """Scan apps/ folder and load all apps with manifest.toml"""
        loaded = []
        
        if not self.apps_dir.exists():
            logger.warning(f"Apps directory not found: {self.apps_dir}")
            self.apps_dir.mkdir(parents=True, exist_ok=True)
            return loaded
        
        for app_path in self.apps_dir.iterdir():
            if app_path.is_dir():
                manifest_file = app_path / "manifest.toml"
                if manifest_file.exists():
                    try:
                        app = self._load_manifest(manifest_file, app_path)
                        if app:
                            self.apps[app.id] = app
                            self._register_commands(app)
                            loaded.append(app.id)
                            logger.info(f"✅ App loaded: {app.id} ({app.name})")
                    except Exception as e:
                        logger.error(f"❌ Failed to load app {app_path.name}: {e}")
        
        logger.info(f"📦 Loaded {len(loaded)} apps: {', '.join(loaded)}")
        return loaded
    
    def _load_manifest(self, manifest_file: Path, app_path: Path) -> Optional[AppManifest]:
        """Load and parse manifest.toml"""
        with open(manifest_file, "rb") as f:
            data = tomllib.load(f)
        
        app_data = data.get("app", {})
        commands_data = data.get("commands", {})
        
        # Extract keywords
        keywords = []
        if "keywords" in commands_data:
            for kw_list in commands_data["keywords"].values():
                keywords.extend(kw_list)
            del commands_data["keywords"]
        
        # Check if app is enabled via .env
        env_file = app_path / ".env"
        enabled = True
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.startswith("APP_ENABLED="):
                        enabled = line.split("=")[1].strip().lower() in ("true", "1", "yes")
        
        app_id = app_data.get("id", app_path.name)
        
        # Create per-app logger
        app_logger = AppLogger(app_id, app_path)
        app_logger.info(f"App loaded: {app_id} v{app_data.get('version', '1.0.0')}")
        
        return AppManifest(
            id=app_id,
            name=app_data.get("name", app_path.name),
            version=app_data.get("version", "1.0.0"),
            description=app_data.get("description", ""),
            language=app_data.get("language", "python"),
            commands=commands_data,
            keywords=keywords,
            scripts=data.get("scripts", {}),
            error_handling=data.get("error_handling", {}),
            service=data.get("service", {}),
            ui=data.get("ui", {}),
            path=app_path,
            enabled=enabled,
            app_logger=app_logger
        )
    
    def _register_commands(self, app: AppManifest):
        """Register app commands and keywords in lookup maps"""
        for cmd in app.commands.keys():
            self._command_map[cmd.lower()] = app.id
        
        for kw in app.keywords:
            self._keyword_map[kw.lower()] = app.id
    
    def get_app(self, app_id: str) -> Optional[AppManifest]:
        """Get app by ID"""
        return self.apps.get(app_id)
    
    def get_all_apps(self) -> Dict[str, AppManifest]:
        """Get all loaded apps"""
        return self.apps
    
    def get_app_for_command(self, command: str) -> Optional[str]:
        """Find app ID for a command"""
        cmd_lower = command.lower()
        
        # Direct match
        if cmd_lower in self._command_map:
            return self._command_map[cmd_lower]
        
        # Partial match
        for pattern, app_id in self._command_map.items():
            if pattern in cmd_lower:
                return app_id
        
        # Keyword match
        for keyword, app_id in self._keyword_map.items():
            if keyword in cmd_lower:
                return app_id
        
        return None
    
    def run_script(self, app_id: str, script_name: str, *args) -> Dict[str, Any]:
        """Run an app script and return result"""
        import time
        start_time = time.time()
        
        app = self.apps.get(app_id)
        if not app:
            return {"success": False, "error": f"App not found: {app_id}"}
        
        script_path = app.scripts.get(script_name)
        if not script_path:
            if app.app_logger:
                app.app_logger.log_error("script_not_found", f"Script not found: {script_name}")
            return {"success": False, "error": f"Script not found: {script_name}"}
        
        full_path = app.path / script_path
        if not full_path.exists():
            if app.app_logger:
                app.app_logger.log_error("file_not_found", f"Script file not found: {full_path}")
            return {"success": False, "error": f"Script file not found: {full_path}"}
        
        try:
            # Determine how to run based on extension
            if full_path.suffix == ".py":
                cmd = ["python3", str(full_path)] + list(args)
            elif full_path.suffix == ".sh":
                cmd = ["bash", str(full_path)] + list(args)
            else:
                cmd = [str(full_path)] + list(args)
            
            result = subprocess.run(
                cmd,
                cwd=str(app.path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Try to parse JSON output
            output = result.stdout.strip()
            try:
                output_data = json.loads(output)
            except json.JSONDecodeError:
                output_data = {"raw": output}
            
            success = result.returncode == 0
            
            # Log to app-specific log
            if app.app_logger:
                app.app_logger.log_script(script_name, duration_ms, success, output[:200] if output else None)
                if not success and result.stderr:
                    app.app_logger.log_error("script_error", result.stderr[:500])
            
            return {
                "success": success,
                "output": output_data,
                "stderr": result.stderr if result.stderr else None,
                "duration_ms": duration_ms
            }
            
        except subprocess.TimeoutExpired:
            if app.app_logger:
                app.app_logger.log_error("timeout", f"Script timeout: {script_name}")
            return {"success": False, "error": "Script timeout"}
        except Exception as e:
            if app.app_logger:
                app.app_logger.log_error("exception", str(e))
            return {"success": False, "error": str(e)}
    
    def run_make(self, app_id: str, target: str, **kwargs) -> Dict[str, Any]:
        """Run Makefile target for an app"""
        import time
        start_time = time.time()
        
        app = self.apps.get(app_id)
        if not app:
            return {"success": False, "error": f"App not found: {app_id}"}
        
        makefile = app.path / "Makefile"
        if not makefile.exists():
            if app.app_logger:
                app.app_logger.log_error("makefile_not_found", "Makefile not found")
            return {"success": False, "error": "Makefile not found"}
        
        try:
            # Build make command with variables
            cmd = ["make", "-C", str(app.path), target]
            for key, value in kwargs.items():
                cmd.append(f"{key.upper()}={value}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            success = result.returncode == 0
            
            # Log to app-specific log
            if app.app_logger:
                app.app_logger.log_script(f"make:{target}", duration_ms, success)
                if not success and result.stderr:
                    app.app_logger.log_error("make_error", result.stderr[:500])
            
            return {
                "success": success,
                "output": result.stdout,
                "stderr": result.stderr if result.stderr else None,
                "duration_ms": duration_ms
            }
            
        except subprocess.TimeoutExpired:
            if app.app_logger:
                app.app_logger.log_error("timeout", f"Make timeout: {target}")
            return {"success": False, "error": "Make timeout"}
        except Exception as e:
            if app.app_logger:
                app.app_logger.log_error("exception", str(e))
            return {"success": False, "error": str(e)}
    
    def get_app_files(self, app_id: str) -> List[Dict[str, Any]]:
        """Get list of files in app for LLM editing"""
        app = self.apps.get(app_id)
        if not app:
            return []
        
        files = []
        for file_path in app.path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                rel_path = file_path.relative_to(app.path)
                files.append({
                    "path": str(rel_path),
                    "full_path": str(file_path),
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix
                })
        
        return files
    
    def read_app_file(self, app_id: str, file_path: str) -> Optional[str]:
        """Read file content from app for LLM editing"""
        app = self.apps.get(app_id)
        if not app:
            return None
        
        full_path = app.path / file_path
        if not full_path.exists() or not full_path.is_file():
            return None
        
        try:
            return full_path.read_text()
        except Exception:
            return None
    
    def write_app_file(self, app_id: str, file_path: str, content: str) -> bool:
        """Write file content to app (LLM editing)"""
        app = self.apps.get(app_id)
        if not app:
            return False
        
        full_path = app.path / file_path
        
        # Security: only allow writing within app directory
        try:
            full_path.resolve().relative_to(app.path.resolve())
        except ValueError:
            logger.warning(f"⚠️ Attempted path traversal: {file_path}")
            return False
        
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            logger.info(f"📝 File written: {app_id}/{file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write file: {e}")
            return False
    
    def get_error_response(self, app_id: str, error_type: str) -> str:
        """Get configured error response for app"""
        app = self.apps.get(app_id)
        if not app:
            return "Błąd aplikacji."
        
        error_key = f"on_{error_type}"
        return app.error_handling.get(
            error_key,
            app.error_handling.get("fallback_response", "Wystąpił błąd.")
        )
    
    def check_app_health(self, app_id: str) -> Dict[str, Any]:
        """Check health of app service"""
        app = self.apps.get(app_id)
        if not app:
            return {"status": "not_found"}
        
        # Try running health check via Makefile
        result = self.run_make(app_id, "health")
        
        if result["success"]:
            app.status = "healthy"
            app.last_error = None
            return {"status": "healthy", "output": result.get("output")}
        else:
            app.status = "error"
            app.last_error = result.get("error") or result.get("stderr")
            return {"status": "error", "error": app.last_error}
    
    def get_apps_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all apps for UI"""
        return [
            {
                "id": app.id,
                "name": app.name,
                "version": app.version,
                "description": app.description,
                "language": app.language,
                "enabled": app.enabled,
                "status": app.status,
                "commands_count": len(app.commands),
                "icon": app.ui.get("icon", "📦"),
                "color": app.ui.get("color", "#6366f1")
            }
            for app in self.apps.values()
        ]
    
    def reload_app(self, app_id: str) -> bool:
        """Reload single app manifest"""
        app = self.apps.get(app_id)
        if not app:
            return False
        
        manifest_file = app.path / "manifest.toml"
        if not manifest_file.exists():
            return False
        
        try:
            new_app = self._load_manifest(manifest_file, app.path)
            if new_app:
                self.apps[app_id] = new_app
                self._register_commands(new_app)
                logger.info(f"🔄 App reloaded: {app_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to reload {app_id}: {e}")
        
        return False
    
    # ==================== APP LOGS ====================
    
    def get_app_logs(self, app_id: str, lines: int = 50) -> Dict[str, Any]:
        """Get recent logs for an app"""
        app = self.apps.get(app_id)
        if not app or not app.app_logger:
            return {"error": f"App not found: {app_id}"}
        
        return {
            "app": app_id,
            "logs": app.app_logger.get_recent_logs(lines),
            "errors": app.app_logger.get_recent_errors(lines // 2),
            "logs_dir": str(app.app_logger.logs_dir)
        }
    
    def get_app_yaml_logs(self, app_id: str) -> str:
        """Get YAML formatted logs for LLM context"""
        app = self.apps.get(app_id)
        if not app or not app.app_logger:
            return ""
        return app.app_logger.get_yaml_logs()
    
    def get_app_errors(self, app_id: str, lines: int = 20) -> List[str]:
        """Get recent errors for an app"""
        app = self.apps.get(app_id)
        if not app or not app.app_logger:
            return []
        return app.app_logger.get_recent_errors(lines)
    
    def log_app_command(self, app_id: str, command: str, result: Any):
        """Log a command execution for an app"""
        app = self.apps.get(app_id)
        if app and app.app_logger:
            app.app_logger.log_command(command, result)
    
    def get_app_context_for_llm(self, app_id: str) -> Dict[str, Any]:
        """Get full app context for LLM debugging/fixing"""
        app = self.apps.get(app_id)
        if not app:
            return {"error": f"App not found: {app_id}"}
        
        # Get all relevant data for LLM to understand app state
        context = {
            "app_id": app.id,
            "name": app.name,
            "version": app.version,
            "language": app.language,
            "status": app.status,
            "last_error": app.last_error,
            "path": str(app.path),
            "files": self.get_app_files(app_id),
            "recent_logs": app.app_logger.get_recent_logs(30) if app.app_logger else [],
            "recent_errors": app.app_logger.get_recent_errors(10) if app.app_logger else [],
            "error_handling": app.error_handling,
            "scripts": app.scripts
        }
        
        return context


# Global registry instance
app_registry = AppRegistry()
