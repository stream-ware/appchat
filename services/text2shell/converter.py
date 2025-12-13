"""
Text2Shell Service - Convert natural language to safe shell commands
Provides controlled shell access for LLM operations
"""

import re
import subprocess
import shlex
from typing import Dict, Any, List, Optional

# Allowed commands whitelist (safe commands only)
ALLOWED_COMMANDS = {
    # System info
    "uname", "hostname", "uptime", "whoami", "id", "date", "cal",
    "df", "du", "free", "top", "ps", "w",
    
    # File operations (read-only)
    "ls", "cat", "head", "tail", "wc", "file", "stat", "find", "locate",
    "grep", "awk", "sed", "sort", "uniq", "cut",
    
    # Network (read-only)
    "ping", "curl", "wget", "ip", "ifconfig", "netstat", "ss",
    
    # Process info
    "pgrep", "pidof",
    
    # Package info (read-only)
    "apt", "dpkg", "pip", "npm",
    
    # Docker (read-only)
    "docker",
    
    # Git (read-only)
    "git",
}

# Blocked patterns for security
BLOCKED_PATTERNS = [
    r"rm\s+-rf",
    r"mkfs",
    r"dd\s+if=",
    r">\s*/dev/",
    r"chmod\s+777",
    r"curl.*\|.*sh",
    r"wget.*\|.*sh",
    r"sudo",
    r"su\s+",
    r"passwd",
    r"\.\.\/",
]

# Command patterns (Polish -> shell)
COMMAND_PATTERNS = {
    # System info
    r"ile pamięci|zużycie ram|memory": "free -h",
    r"ile miejsca|dysk|disk": "df -h",
    r"czas działania|uptime": "uptime",
    r"jaki system|wersja systemu": "uname -a",
    r"kto jest zalogowany|who": "w",
    r"procesy|lista procesów|ps": "ps aux --sort=-%mem | head -20",
    r"data|dzisiaj|today": "date",
    
    # Network
    r"ping\s+(.+)": "ping -c 4 {0}",
    r"ip\s+adres|mój ip|ip address": "ip addr show",
    r"porty|otwarte porty|ports": "ss -tuln",
    
    # Docker
    r"kontenery|docker ps": "docker ps -a",
    r"obrazy docker|docker images": "docker images",
    
    # Git
    r"git status": "git status",
    r"git log": "git log --oneline -10",
    r"git branch": "git branch -a",
    
    # Files
    r"pokaż\s+(.+)": "cat {0}",
    r"lista\s+w?\s*(.*)": "ls -la {0}",
    r"znajdź\s+(.+)": "find . -name '*{0}*' 2>/dev/null | head -20",
    r"rozmiar\s+(.+)": "du -sh {0}",
}


class Text2Shell:
    """Convert natural language to safe shell commands"""
    
    @classmethod
    def text2shell(cls, text: str, role: str = "user", cwd: str = None) -> Dict[str, Any]:
        """
        Convert natural language to shell command
        
        Args:
            text: Natural language command
            role: User role (user/manager/admin)
            cwd: Working directory
        
        Returns:
            {"success": bool, "command": str, "safe": bool}
        """
        text_lower = text.lower().strip()
        
        # Security check
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, text_lower):
                return {
                    "success": False,
                    "error": "Blocked command",
                    "message": "Ta komenda jest zablokowana ze względów bezpieczeństwa"
                }
        
        # Try to match patterns
        for pattern, cmd_template in COMMAND_PATTERNS.items():
            match = re.search(pattern, text_lower)
            if match:
                # Build command
                cmd = cmd_template
                for i, group in enumerate(match.groups()):
                    cmd = cmd.replace(f"{{{i}}}", shlex.quote(group) if group else "")
                
                # Validate command
                base_cmd = cmd.split()[0] if cmd else ""
                if base_cmd not in ALLOWED_COMMANDS:
                    return {
                        "success": False,
                        "error": "Command not allowed",
                        "message": f"Komenda '{base_cmd}' nie jest dozwolona"
                    }
                
                return {
                    "success": True,
                    "command": cmd.strip(),
                    "safe": True,
                    "original": text
                }
        
        # Try direct command extraction
        direct_cmd = cls._extract_direct_command(text)
        if direct_cmd:
            base_cmd = direct_cmd.split()[0]
            if base_cmd in ALLOWED_COMMANDS:
                return {
                    "success": True,
                    "command": direct_cmd,
                    "safe": True,
                    "original": text
                }
        
        return {
            "success": False,
            "error": "Could not parse command",
            "message": f"Nie rozumiem komendy: {text}"
        }
    
    @classmethod
    def _extract_direct_command(cls, text: str) -> Optional[str]:
        """Try to extract a direct shell command from text"""
        # Check for "wykonaj X" or "uruchom X" patterns
        patterns = [
            r"wykonaj\s+(.+)",
            r"uruchom\s+(.+)",
            r"run\s+(.+)",
            r"exec\s+(.+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
        
        return None
    
    @classmethod
    def execute(cls, command: str, cwd: str = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute shell command safely
        
        Args:
            command: Shell command to execute
            cwd: Working directory
            timeout: Timeout in seconds
        
        Returns:
            {"success": bool, "stdout": str, "stderr": str, "returncode": int}
        """
        # Final security check
        base_cmd = command.split()[0] if command else ""
        if base_cmd not in ALLOWED_COMMANDS:
            return {
                "success": False,
                "error": f"Command not in whitelist: {base_cmd}"
            }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:10000],  # Limit output
                "stderr": result.stderr[:2000],
                "returncode": result.returncode,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "timeout",
                "message": f"Komenda przekroczyła limit czasu ({timeout}s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class Shell2Text:
    """Convert shell output to natural language"""
    
    @classmethod
    def shell2text(cls, result: Dict[str, Any], command: str) -> str:
        """Convert shell command result to natural language"""
        if not result.get("success"):
            error = result.get("error", result.get("stderr", "Nieznany błąd"))
            return f"❌ Błąd wykonania: {error}"
        
        stdout = result.get("stdout", "").strip()
        command_base = command.split()[0] if command else ""
        
        # Format based on command type
        if command_base == "free":
            return cls._format_memory(stdout)
        elif command_base == "df":
            return cls._format_disk(stdout)
        elif command_base == "uptime":
            return cls._format_uptime(stdout)
        elif command_base == "ps":
            return cls._format_processes(stdout)
        elif command_base in ["ls", "find"]:
            return cls._format_files(stdout)
        elif command_base == "ping":
            return cls._format_ping(stdout)
        elif command_base == "docker":
            return cls._format_docker(stdout)
        else:
            # Default formatting
            if len(stdout) > 500:
                return f"```\n{stdout[:500]}\n... ({len(stdout) - 500} więcej znaków)\n```"
            return f"```\n{stdout}\n```" if stdout else "Brak wyniku"
    
    @classmethod
    def _format_memory(cls, output: str) -> str:
        """Format 'free' command output"""
        lines = output.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 4:
                total, used, free = parts[1], parts[2], parts[3]
                return f"💾 Pamięć RAM:\n   Całkowita: {total}\n   Używana: {used}\n   Wolna: {free}"
        return output
    
    @classmethod
    def _format_disk(cls, output: str) -> str:
        """Format 'df' command output"""
        lines = output.strip().split("\n")[1:]  # Skip header
        result = ["💿 Miejsce na dysku:"]
        for line in lines[:5]:  # First 5 filesystems
            parts = line.split()
            if len(parts) >= 5:
                fs, size, used, avail, pct = parts[0], parts[1], parts[2], parts[3], parts[4]
                result.append(f"   {fs}: {used}/{size} ({pct})")
        return "\n".join(result)
    
    @classmethod
    def _format_uptime(cls, output: str) -> str:
        """Format 'uptime' command output"""
        return f"⏱️ {output.strip()}"
    
    @classmethod
    def _format_processes(cls, output: str) -> str:
        """Format 'ps' command output"""
        lines = output.strip().split("\n")
        result = [f"📊 Top {min(10, len(lines)-1)} procesów:"]
        for line in lines[1:11]:  # Skip header, first 10
            parts = line.split()
            if len(parts) >= 11:
                user, pid, cpu, mem = parts[0], parts[1], parts[2], parts[3]
                cmd = " ".join(parts[10:])[:30]
                result.append(f"   {pid}: {cmd} (CPU: {cpu}%, MEM: {mem}%)")
        return "\n".join(result)
    
    @classmethod
    def _format_files(cls, output: str) -> str:
        """Format file listing output"""
        lines = output.strip().split("\n")
        if len(lines) > 20:
            return f"📁 Znaleziono {len(lines)} elementów:\n" + "\n".join(lines[:20]) + f"\n... i {len(lines) - 20} więcej"
        return f"📁 Znaleziono {len(lines)} elementów:\n" + "\n".join(lines)
    
    @classmethod
    def _format_ping(cls, output: str) -> str:
        """Format ping output"""
        # Extract stats
        if "packets transmitted" in output:
            stats_line = [l for l in output.split("\n") if "packets transmitted" in l]
            if stats_line:
                return f"🌐 Ping: {stats_line[0]}"
        return f"🌐 {output[:200]}"
    
    @classmethod
    def _format_docker(cls, output: str) -> str:
        """Format docker output"""
        lines = output.strip().split("\n")
        if len(lines) > 1:
            return f"🐳 Docker ({len(lines)-1} kontenerów/obrazów):\n" + "\n".join(lines[:10])
        return f"🐳 {output}"


# Singleton instances
text2shell = Text2Shell()
shell2text = Shell2Text()
