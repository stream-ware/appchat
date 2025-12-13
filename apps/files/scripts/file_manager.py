#!/usr/bin/env python3
"""
File Manager - Access and manage user files
Uses text2filesystem service for natural language processing
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"

# Import text2filesystem service
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from services.text2filesystem.converter import text2filesystem, filesystem2text, Text2Filesystem

# Allowed directories
ALLOWED_DIRS = [
    Path.home() / "Documents",
    Path.home() / "Downloads", 
    Path.home() / "Pictures",
]


def list_directory(path: str = None) -> Dict[str, Any]:
    """List files in directory"""
    if not path:
        path = str(Path.home() / "Documents")
    
    result = Text2Filesystem.execute("list", path)
    return result


def search_files(pattern: str) -> Dict[str, Any]:
    """Search for files matching pattern"""
    result = Text2Filesystem.execute("search", str(Path.home()), {"groups": (pattern,)})
    return result


def get_file_info(path: str) -> Dict[str, Any]:
    """Get information about a file"""
    result = Text2Filesystem.execute("info", path)
    return result


def read_file(path: str) -> Dict[str, Any]:
    """Read text file contents"""
    result = Text2Filesystem.execute("read", path)
    return result


def get_recent_files(limit: int = 20) -> Dict[str, Any]:
    """Get recently modified files"""
    recent = []
    
    for allowed_dir in ALLOWED_DIRS:
        if allowed_dir.exists():
            for f in allowed_dir.rglob("*"):
                if f.is_file():
                    try:
                        stat = f.stat()
                        recent.append({
                            "path": str(f),
                            "name": f.name,
                            "modified": stat.st_mtime,
                            "size": stat.st_size
                        })
                    except:
                        pass
    
    # Sort by modification time, most recent first
    recent.sort(key=lambda x: x["modified"], reverse=True)
    recent = recent[:limit]
    
    # Format timestamps
    for f in recent:
        f["modified"] = datetime.fromtimestamp(f["modified"]).isoformat()
        f["size_human"] = _human_size(f["size"])
    
    return {
        "success": True,
        "count": len(recent),
        "files": recent
    }


def get_folder_size(path: str) -> Dict[str, Any]:
    """Calculate folder size"""
    path = Path(path)
    if not path.exists():
        return {"success": False, "error": f"Path not found: {path}"}
    
    total_size = 0
    file_count = 0
    
    if path.is_dir():
        for f in path.rglob("*"):
            if f.is_file():
                total_size += f.stat().st_size
                file_count += 1
    else:
        total_size = path.stat().st_size
        file_count = 1
    
    return {
        "success": True,
        "path": str(path),
        "size": total_size,
        "size_human": _human_size(total_size),
        "file_count": file_count
    }


def process_command(text: str, role: str = "user") -> Dict[str, Any]:
    """Process natural language file command"""
    result = text2filesystem.text2filesystem(text, role)
    
    if result.get("success"):
        operation = result.get("operation")
        path = result.get("path")
        params = result.get("params", {})
        
        exec_result = Text2Filesystem.execute(operation, path, params)
        
        return {
            "success": True,
            "operation": operation,
            "result": exec_result,
            "text_response": filesystem2text.filesystem2text(exec_result, operation)
        }
    
    return result


def _human_size(size: int) -> str:
    """Convert bytes to human readable size"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default: list Documents
        result = list_directory()
    else:
        action = sys.argv[1]
        
        if action == "list":
            path = sys.argv[2] if len(sys.argv) > 2 else None
            result = list_directory(path)
        elif action == "search":
            pattern = sys.argv[2] if len(sys.argv) > 2 else "*"
            result = search_files(pattern)
        elif action == "info":
            path = sys.argv[2] if len(sys.argv) > 2 else "."
            result = get_file_info(path)
        elif action == "read":
            path = sys.argv[2] if len(sys.argv) > 2 else None
            result = read_file(path) if path else {"error": "Path required"}
        elif action == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            result = get_recent_files(limit)
        elif action == "size":
            path = sys.argv[2] if len(sys.argv) > 2 else "."
            result = get_folder_size(path)
        elif action == "query":
            # Natural language query
            text = " ".join(sys.argv[2:])
            role = os.getenv("USER_ROLE", "user")
            result = process_command(text, role)
        else:
            result = {"error": f"Unknown action: {action}"}
    
    print(json.dumps(result, indent=2, default=str))
