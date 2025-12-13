"""
Text2Filesystem Service - Convert natural language to filesystem operations
Provides safe access to user files in allowed directories
"""

import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Allowed base directories (configurable)
ALLOWED_DIRS = [
    Path.home() / "Documents",
    Path.home() / "Downloads",
    Path.home() / "Pictures",
]

# Blocked patterns for security
BLOCKED_PATTERNS = [
    r"\.\.\/",  # Parent directory traversal
    r"\/etc\/",
    r"\/root\/",
    r"\/var\/",
    r"\.ssh",
    r"\.gnupg",
    r"\.config\/",
]


class Text2Filesystem:
    """Convert natural language to filesystem operations"""
    
    # Operation patterns
    PATTERNS = {
        # List operations
        r"pokaż pliki w?\s*(.*)": ("list", None),
        r"lista plików w?\s*(.*)": ("list", None),
        r"co jest w\s+(.+)": ("list", None),
        r"zawartość\s+(.+)": ("list", None),
        
        # Search operations
        r"znajdź\s+(.+)": ("search", None),
        r"szukaj\s+(.+)": ("search", None),
        r"gdzie jest\s+(.+)": ("search", None),
        
        # Read operations
        r"pokaż zawartość\s+(.+)": ("read", None),
        r"otwórz\s+(.+)": ("read", None),
        r"przeczytaj\s+(.+)": ("read", None),
        
        # Info operations
        r"informacje o\s+(.+)": ("info", None),
        r"rozmiar\s+(.+)": ("info", None),
        r"ile zajmuje\s+(.+)": ("info", None),
        
        # Create operations (manager/admin)
        r"utwórz folder\s+(.+)": ("mkdir", "manager"),
        r"stwórz katalog\s+(.+)": ("mkdir", "manager"),
        
        # Copy/Move operations (admin)
        r"kopiuj\s+(.+)\s+do\s+(.+)": ("copy", "admin"),
        r"przenieś\s+(.+)\s+do\s+(.+)": ("move", "admin"),
        
        # Delete operations (admin only)
        r"usuń\s+(.+)": ("delete", "admin"),
        r"skasuj\s+(.+)": ("delete", "admin"),
    }
    
    # Directory aliases
    DIR_ALIASES = {
        "dokumenty": "Documents",
        "documents": "Documents",
        "pobrane": "Downloads",
        "downloads": "Downloads",
        "zdjęcia": "Pictures",
        "obrazy": "Pictures",
        "pictures": "Pictures",
        "pulpit": "Desktop",
        "desktop": "Desktop",
        "home": "",
        "dom": "",
    }
    
    @classmethod
    def text2filesystem(cls, text: str, role: str = "user") -> Dict[str, Any]:
        """
        Convert natural language to filesystem operation
        
        Args:
            text: Natural language command
            role: User role (user/manager/admin)
        
        Returns:
            {"success": bool, "operation": str, "path": str, "params": dict}
        """
        text_lower = text.lower().strip()
        
        # Security check
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, text_lower):
                return {
                    "success": False,
                    "error": "Security violation",
                    "message": "Dostęp do tej ścieżki jest zabroniony"
                }
        
        # Try to match patterns
        for pattern, (operation, required_role) in cls.PATTERNS.items():
            match = re.search(pattern, text_lower)
            if match:
                # Check permissions
                if required_role and role not in [required_role, "admin"]:
                    return {
                        "success": False,
                        "error": "Permission denied",
                        "message": f"Operacja {operation} wymaga uprawnień {required_role}"
                    }
                
                # Extract path
                path = cls._resolve_path(match.group(1) if match.groups() else "")
                
                return {
                    "success": True,
                    "operation": operation,
                    "path": str(path) if path else None,
                    "params": {"groups": match.groups()},
                    "original": text
                }
        
        # Default: list home documents
        return {
            "success": True,
            "operation": "list",
            "path": str(Path.home() / "Documents"),
            "params": {},
            "original": text
        }
    
    @classmethod
    def _resolve_path(cls, path_text: str) -> Optional[Path]:
        """Resolve path from text, applying aliases and security checks"""
        if not path_text:
            return Path.home() / "Documents"
        
        path_text = path_text.strip()
        
        # Check aliases
        for alias, real in cls.DIR_ALIASES.items():
            if path_text.startswith(alias):
                path_text = path_text.replace(alias, real, 1)
                break
        
        # Build path
        if path_text.startswith("/"):
            path = Path(path_text)
        elif path_text.startswith("~"):
            path = Path(path_text).expanduser()
        else:
            path = Path.home() / path_text
        
        # Security: ensure path is within allowed directories
        path = path.resolve()
        if not any(cls._is_subpath(path, allowed) for allowed in ALLOWED_DIRS):
            # Allow home directory listing
            if path == Path.home():
                return path
            return None
        
        return path
    
    @classmethod
    def _is_subpath(cls, path: Path, parent: Path) -> bool:
        """Check if path is under parent directory"""
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False
    
    @classmethod
    def execute(cls, operation: str, path: str, params: dict = None) -> Dict[str, Any]:
        """Execute filesystem operation and return results"""
        path = Path(path) if path else Path.home() / "Documents"
        params = params or {}
        
        try:
            if operation == "list":
                return cls._list_dir(path)
            elif operation == "search":
                return cls._search_files(path, params.get("groups", ["*"])[0])
            elif operation == "read":
                return cls._read_file(path)
            elif operation == "info":
                return cls._file_info(path)
            elif operation == "mkdir":
                return cls._make_dir(path)
            elif operation == "copy":
                dest = params.get("groups", [None, None])[1]
                return cls._copy_file(path, dest)
            elif operation == "move":
                dest = params.get("groups", [None, None])[1]
                return cls._move_file(path, dest)
            elif operation == "delete":
                return cls._delete_file(path)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @classmethod
    def _list_dir(cls, path: Path) -> Dict[str, Any]:
        """List directory contents"""
        if not path.exists():
            return {"success": False, "error": f"Ścieżka nie istnieje: {path}"}
        
        if not path.is_dir():
            return {"success": False, "error": f"Nie jest katalogiem: {path}"}
        
        items = []
        for item in sorted(path.iterdir()):
            try:
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": stat.st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except:
                items.append({"name": item.name, "type": "unknown"})
        
        return {
            "success": True,
            "path": str(path),
            "count": len(items),
            "items": items[:50]  # Limit to 50 items
        }
    
    @classmethod
    def _search_files(cls, base_path: Path, pattern: str) -> Dict[str, Any]:
        """Search for files matching pattern"""
        results = []
        pattern = pattern.strip() if pattern else "*"
        
        for allowed in ALLOWED_DIRS:
            if allowed.exists():
                for match in allowed.rglob(f"*{pattern}*"):
                    if len(results) >= 50:
                        break
                    results.append({
                        "path": str(match),
                        "name": match.name,
                        "type": "dir" if match.is_dir() else "file"
                    })
        
        return {
            "success": True,
            "pattern": pattern,
            "count": len(results),
            "results": results
        }
    
    @classmethod
    def _read_file(cls, path: Path) -> Dict[str, Any]:
        """Read file contents (text files only, limited size)"""
        if not path.exists():
            return {"success": False, "error": f"Plik nie istnieje: {path}"}
        
        if not path.is_file():
            return {"success": False, "error": f"Nie jest plikiem: {path}"}
        
        # Size limit: 100KB
        if path.stat().st_size > 100 * 1024:
            return {"success": False, "error": "Plik zbyt duży (max 100KB)"}
        
        # Only text files
        text_extensions = {".txt", ".md", ".json", ".csv", ".log", ".py", ".js", ".html", ".css", ".yaml", ".yml", ".toml"}
        if path.suffix.lower() not in text_extensions:
            return {"success": False, "error": f"Nieobsługiwany typ pliku: {path.suffix}"}
        
        try:
            content = path.read_text(encoding="utf-8")
            return {
                "success": True,
                "path": str(path),
                "size": len(content),
                "content": content[:5000]  # First 5000 chars
            }
        except UnicodeDecodeError:
            return {"success": False, "error": "Nie można odczytać pliku (nie jest tekstem)"}
    
    @classmethod
    def _file_info(cls, path: Path) -> Dict[str, Any]:
        """Get file/directory info"""
        if not path.exists():
            return {"success": False, "error": f"Ścieżka nie istnieje: {path}"}
        
        stat = path.stat()
        info = {
            "success": True,
            "path": str(path),
            "name": path.name,
            "type": "dir" if path.is_dir() else "file",
            "size": stat.st_size,
            "size_human": cls._human_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }
        
        if path.is_dir():
            info["items_count"] = len(list(path.iterdir()))
        
        return info
    
    @classmethod
    def _make_dir(cls, path: Path) -> Dict[str, Any]:
        """Create directory"""
        path.mkdir(parents=True, exist_ok=True)
        return {"success": True, "message": f"Utworzono katalog: {path}"}
    
    @classmethod
    def _copy_file(cls, src: Path, dest: str) -> Dict[str, Any]:
        """Copy file"""
        dest_path = cls._resolve_path(dest)
        if not dest_path:
            return {"success": False, "error": "Nieprawidłowa ścieżka docelowa"}
        shutil.copy2(src, dest_path)
        return {"success": True, "message": f"Skopiowano {src} do {dest_path}"}
    
    @classmethod
    def _move_file(cls, src: Path, dest: str) -> Dict[str, Any]:
        """Move file"""
        dest_path = cls._resolve_path(dest)
        if not dest_path:
            return {"success": False, "error": "Nieprawidłowa ścieżka docelowa"}
        shutil.move(str(src), str(dest_path))
        return {"success": True, "message": f"Przeniesiono {src} do {dest_path}"}
    
    @classmethod
    def _delete_file(cls, path: Path) -> Dict[str, Any]:
        """Delete file or directory"""
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return {"success": True, "message": f"Usunięto: {path}"}
    
    @staticmethod
    def _human_size(size: int) -> str:
        """Convert bytes to human readable size"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class Filesystem2Text:
    """Convert filesystem results to natural language"""
    
    @classmethod
    def filesystem2text(cls, result: Dict[str, Any], operation: str) -> str:
        """Convert filesystem operation result to natural language"""
        if not result.get("success"):
            return f"❌ Błąd: {result.get('error', 'Nieznany błąd')}"
        
        if operation == "list":
            return cls._format_list(result)
        elif operation == "search":
            return cls._format_search(result)
        elif operation == "read":
            return cls._format_read(result)
        elif operation == "info":
            return cls._format_info(result)
        else:
            return result.get("message", "Operacja wykonana pomyślnie")
    
    @classmethod
    def _format_list(cls, result: Dict) -> str:
        """Format directory listing"""
        items = result.get("items", [])
        path = result.get("path", "")
        
        dirs = [i for i in items if i.get("type") == "dir"]
        files = [i for i in items if i.get("type") == "file"]
        
        lines = [f"📁 {path}"]
        lines.append(f"   {len(dirs)} folderów, {len(files)} plików")
        
        for d in dirs[:5]:
            lines.append(f"   📂 {d['name']}/")
        for f in files[:10]:
            size = Text2Filesystem._human_size(f.get("size", 0))
            lines.append(f"   📄 {f['name']} ({size})")
        
        if len(items) > 15:
            lines.append(f"   ... i {len(items) - 15} więcej")
        
        return "\n".join(lines)
    
    @classmethod
    def _format_search(cls, result: Dict) -> str:
        """Format search results"""
        results = result.get("results", [])
        pattern = result.get("pattern", "")
        
        if not results:
            return f"🔍 Nie znaleziono plików pasujących do: {pattern}"
        
        lines = [f"🔍 Znaleziono {len(results)} wyników dla: {pattern}"]
        for r in results[:10]:
            icon = "📂" if r.get("type") == "dir" else "📄"
            lines.append(f"   {icon} {r['name']}")
        
        return "\n".join(lines)
    
    @classmethod
    def _format_read(cls, result: Dict) -> str:
        """Format file content"""
        content = result.get("content", "")
        path = result.get("path", "")
        
        lines = [f"📄 {path}"]
        lines.append("─" * 40)
        lines.append(content[:1000])  # First 1000 chars
        if len(content) > 1000:
            lines.append(f"... ({len(content) - 1000} więcej znaków)")
        
        return "\n".join(lines)
    
    @classmethod
    def _format_info(cls, result: Dict) -> str:
        """Format file info"""
        return f"""📋 Informacje o pliku:
   Nazwa: {result.get('name')}
   Typ: {'Folder' if result.get('type') == 'dir' else 'Plik'}
   Rozmiar: {result.get('size_human')}
   Zmodyfikowany: {result.get('modified', '')[:19]}"""


# Singleton instances
text2filesystem = Text2Filesystem()
filesystem2text = Filesystem2Text()
