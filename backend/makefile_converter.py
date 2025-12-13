"""
Streamware Makefile Converter
text2makefile / makefile2text - Standardized communication format
Converts between natural language and Makefile targets
"""

import re
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger("streamware.makefile")


@dataclass
class MakeTarget:
    """Parsed Makefile target"""
    name: str
    description: str
    params: List[str]
    makefile_type: str  # run, user, admin
    example: str = ""


class MakefileConverter:
    """
    Bidirectional converter between natural language and Makefile commands
    
    text2makefile: "pokaż pogodę" -> "make -f Makefile.user pogoda"
    makefile2text: "make -f Makefile.admin set-timeout SEC=30" -> "Ustaw timeout na 30 sekund"
    """
    
    # Makefile types by role
    MAKEFILE_TYPES = {
        "run": {"file": "Makefile.run", "role": "system", "description": "System/DevOps commands"},
        "user": {"file": "Makefile.user", "role": "user", "description": "Daily use commands"},
        "admin": {"file": "Makefile.admin", "role": "admin", "description": "Configuration commands"},
    }
    
    # Natural language patterns -> make targets
    TEXT_TO_MAKE_PATTERNS = {
        # Weather app patterns - city first (more specific)
        r"pogoda.*(w|dla)\s+(\w+)": ("user", "city", {"CITY": "{1}"}),
        r"weather.*(in|for)\s+(\w+)": ("user", "city", {"CITY": "{1}"}),
        r"(pokaż|sprawdź|jaka).*(pogod|weather)": ("user", "pogoda", {}),
        r"(temperatura|temp)": ("user", "temp", {}),
        r"(prognoz|forecast).*?(\d+)": ("user", "forecast", {"DAYS": "{1}"}),
        
        # Admin patterns - specific first
        r"(ustaw|set).*(timeout|czas).*?(\d+)": ("admin", "set-timeout", {"SEC": "{2}"}),
        r"(ustaw|set).*(miasto|city)\s+(\w+)": ("admin", "set-default-city", {"CITY": "{2}"}),
        r"(włącz|enable)": ("admin", "enable", {}),
        r"(wyłącz|disable)": ("admin", "disable", {}),
        r"(konfiguracja|config)": ("admin", "config", {}),
        r"(backup|kopia)": ("admin", "backup", {}),
        r"(test|sprawdź).*(api|połączenie)": ("admin", "test", {}),
        
        # System patterns
        r"(start|uruchom)\s*(app|aplik)?": ("run", "start", {}),
        r"(stop|zatrzymaj)": ("run", "stop", {}),
        r"(restart|restartuj)": ("run", "restart", {}),
        r"(status|stan)": ("run", "status", {}),
        r"(health|zdrowie)": ("run", "health", {}),
        r"(log|logi)": ("run", "logs", {}),
        r"(install|instaluj)": ("run", "install", {}),
    }
    
    def __init__(self, apps_dir: Path = None):
        self.apps_dir = apps_dir or Path(__file__).parent.parent / "apps"
        self._target_cache: Dict[str, Dict[str, List[MakeTarget]]] = {}
    
    def parse_makefile(self, makefile_path: Path) -> List[MakeTarget]:
        """Parse Makefile and extract targets with descriptions"""
        targets = []
        
        if not makefile_path.exists():
            return targets
        
        content = makefile_path.read_text()
        makefile_type = makefile_path.stem.split(".")[-1] if "." in makefile_path.name else "main"
        
        # Parse @text annotations
        text_annotations = {}
        for match in re.finditer(r'#\s*@text\s+(\w+):\s*"([^"]+)"', content):
            text_annotations[match.group(1)] = match.group(2)
        
        # Parse .PHONY targets
        phony_match = re.search(r'\.PHONY:\s*(.+)', content)
        phony_targets = phony_match.group(1).split() if phony_match else []
        
        # Parse target definitions
        for match in re.finditer(r'^(\w[\w-]*):\s*(?:.*)?$\n((?:\t.*\n?)*)', content, re.MULTILINE):
            target_name = match.group(1)
            target_body = match.group(2)
            
            # Skip internal targets
            if target_name.startswith("_") or target_name in ["help"]:
                continue
            
            # Get description from @text annotation or generate from body
            description = text_annotations.get(target_name, "")
            if not description:
                # Try to extract from echo in body
                echo_match = re.search(r'echo\s+"([^"]+)"', target_body)
                if echo_match:
                    description = echo_match.group(1)
            
            # Extract parameters (VAR=... patterns)
            params = re.findall(r'\$\((\w+)\)', target_body)
            params = [p for p in params if p not in ["APP_DIR", "APP_NAME", "SCRIPTS"]]
            
            targets.append(MakeTarget(
                name=target_name,
                description=description,
                params=params,
                makefile_type=makefile_type,
                example=f"make -f {makefile_path.name} {target_name}" + 
                        (" " + " ".join(f"{p}=..." for p in params) if params else "")
            ))
        
        return targets
    
    def load_app_makefiles(self, app_id: str) -> Dict[str, List[MakeTarget]]:
        """Load all Makefiles for an app"""
        if app_id in self._target_cache:
            return self._target_cache[app_id]
        
        app_path = self.apps_dir / app_id
        if not app_path.exists():
            return {}
        
        result = {}
        for mtype, minfo in self.MAKEFILE_TYPES.items():
            makefile_path = app_path / minfo["file"]
            if makefile_path.exists():
                result[mtype] = self.parse_makefile(makefile_path)
        
        # Also parse main Makefile
        main_makefile = app_path / "Makefile"
        if main_makefile.exists():
            result["main"] = self.parse_makefile(main_makefile)
        
        self._target_cache[app_id] = result
        return result
    
    def text2makefile(self, text: str, app_id: str = None, role: str = "user") -> Dict[str, Any]:
        """
        Convert natural language to Makefile command
        
        Args:
            text: Natural language input
            app_id: Target app (optional, auto-detect if not provided)
            role: user/admin/system - determines which Makefile to use
        
        Returns:
            {
                "success": bool,
                "command": "make -f Makefile.user pogoda",
                "target": "pogoda",
                "params": {"CITY": "Warsaw"},
                "makefile": "Makefile.user",
                "description": "Pokaż aktualną pogodę"
            }
        """
        text_lower = text.lower().strip()
        
        # Try pattern matching
        for pattern, (mtype, target, param_template) in self.TEXT_TO_MAKE_PATTERNS.items():
            match = re.search(pattern, text_lower)
            if match:
                # Extract parameters from regex groups
                params = {}
                for param_name, group_ref in param_template.items():
                    if group_ref.startswith("{") and group_ref.endswith("}"):
                        group_idx = int(group_ref[1:-1])
                        if group_idx < len(match.groups()):
                            params[param_name] = match.group(group_idx + 1)
                    else:
                        params[param_name] = group_ref
                
                makefile = self.MAKEFILE_TYPES[mtype]["file"]
                
                # Build command
                cmd_parts = ["make", "-f", makefile, target]
                for k, v in params.items():
                    cmd_parts.append(f"{k}={v}")
                
                return {
                    "success": True,
                    "command": " ".join(cmd_parts),
                    "target": target,
                    "params": params,
                    "makefile": makefile,
                    "makefile_type": mtype,
                    "description": f"Execute {target} with params {params}" if params else f"Execute {target}"
                }
        
        # Fallback: try to find matching target in app's Makefiles
        if app_id:
            makefiles = self.load_app_makefiles(app_id)
            for mtype, targets in makefiles.items():
                for target in targets:
                    # Check if target name matches text
                    if target.name in text_lower or text_lower in target.name:
                        makefile = self.MAKEFILE_TYPES.get(mtype, {}).get("file", "Makefile")
                        return {
                            "success": True,
                            "command": f"make -f {makefile} {target.name}",
                            "target": target.name,
                            "params": {},
                            "makefile": makefile,
                            "makefile_type": mtype,
                            "description": target.description
                        }
        
        return {
            "success": False,
            "error": f"Could not parse: '{text}'",
            "suggestions": self.get_suggestions(app_id, role)
        }
    
    def makefile2text(self, command: str, app_id: str = None) -> Dict[str, Any]:
        """
        Convert Makefile command to natural language description
        
        Args:
            command: "make -f Makefile.user city CITY=Krakow"
            app_id: App context (optional)
        
        Returns:
            {
                "success": bool,
                "text": "Sprawdź pogodę dla Krakowa",
                "target": "city",
                "params": {"CITY": "Krakow"}
            }
        """
        # Parse make command
        parts = command.split()
        
        # Find makefile and target
        makefile = "Makefile"
        target = None
        params = {}
        
        i = 0
        while i < len(parts):
            if parts[i] == "make":
                i += 1
                continue
            elif parts[i] == "-f" and i + 1 < len(parts):
                makefile = parts[i + 1]
                i += 2
                continue
            elif parts[i] == "-C" and i + 1 < len(parts):
                i += 2  # Skip directory
                continue
            elif "=" in parts[i]:
                key, value = parts[i].split("=", 1)
                params[key] = value
            else:
                target = parts[i]
            i += 1
        
        if not target:
            return {"success": False, "error": "No target found in command"}
        
        # Generate human-readable text
        makefile_type = makefile.split(".")[-1] if "." in makefile else "main"
        
        # Build description
        text_parts = []
        
        # Target-specific descriptions
        target_texts = {
            "pogoda": "Pokaż aktualną pogodę",
            "weather": "Show current weather",
            "city": f"Sprawdź pogodę dla {params.get('CITY', '?')}",
            "temp": "Pokaż temperaturę",
            "forecast": f"Pokaż prognozę na {params.get('DAYS', '?')} dni",
            "start": "Uruchom aplikację",
            "stop": "Zatrzymaj aplikację",
            "restart": "Restartuj aplikację",
            "status": "Sprawdź status",
            "health": "Sprawdź zdrowie serwisu",
            "config": "Pokaż konfigurację",
            "enable": "Włącz aplikację",
            "disable": "Wyłącz aplikację",
            "set-timeout": f"Ustaw timeout na {params.get('SEC', '?')} sekund",
            "set-default-city": f"Ustaw domyślne miasto: {params.get('CITY', '?')}",
            "backup": "Zrób kopię zapasową konfiguracji",
            "test": "Przetestuj połączenie z API",
        }
        
        text = target_texts.get(target, f"Wykonaj: {target}")
        
        return {
            "success": True,
            "text": text,
            "target": target,
            "params": params,
            "makefile": makefile,
            "makefile_type": makefile_type,
            "role": self.MAKEFILE_TYPES.get(makefile_type, {}).get("role", "unknown")
        }
    
    def get_suggestions(self, app_id: str = None, role: str = "user") -> List[Dict[str, str]]:
        """Get available commands as suggestions"""
        suggestions = []
        
        if app_id:
            makefiles = self.load_app_makefiles(app_id)
            
            # Filter by role
            mtype = {"user": "user", "admin": "admin", "system": "run"}.get(role, "user")
            
            if mtype in makefiles:
                for target in makefiles[mtype]:
                    suggestions.append({
                        "command": target.example,
                        "text": target.description or target.name,
                        "target": target.name
                    })
        
        return suggestions
    
    def get_all_commands(self, app_id: str) -> Dict[str, List[Dict]]:
        """Get all commands organized by role"""
        makefiles = self.load_app_makefiles(app_id)
        
        result = {}
        for mtype, targets in makefiles.items():
            role = self.MAKEFILE_TYPES.get(mtype, {}).get("role", mtype)
            result[role] = [
                {
                    "target": t.name,
                    "description": t.description,
                    "params": t.params,
                    "example": t.example
                }
                for t in targets
            ]
        
        return result
    
    def execute(self, app_id: str, text_or_command: str, is_text: bool = True) -> Dict[str, Any]:
        """
        Execute a command (from text or make command)
        
        Args:
            app_id: Target app
            text_or_command: Natural language or make command
            is_text: True if input is natural language
        """
        # Convert if needed
        if is_text:
            conversion = self.text2makefile(text_or_command, app_id)
            if not conversion["success"]:
                return conversion
            command = conversion["command"]
        else:
            command = text_or_command
        
        # Execute
        app_path = self.apps_dir / app_id
        if not app_path.exists():
            return {"success": False, "error": f"App not found: {app_id}"}
        
        try:
            result = subprocess.run(
                command.split(),
                cwd=str(app_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "output": result.stdout.strip(),
                "stderr": result.stderr if result.stderr else None
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global converter instance
makefile_converter = MakefileConverter()
