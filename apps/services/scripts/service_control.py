#!/usr/bin/env python3
"""Control system services (start, stop, restart)"""

import subprocess
import json
import sys

def control_service(action: str, name: str) -> dict:
    """Control systemd service"""
    if action not in ["start", "stop", "restart", "enable", "disable"]:
        return {"success": False, "error": f"Invalid action: {action}"}
    
    try:
        result = subprocess.run(
            ["sudo", "systemctl", action, name],
            capture_output=True, text=True, timeout=30
        )
        
        success = result.returncode == 0
        
        # Get new status
        status = subprocess.run(
            ["systemctl", "is-active", name],
            capture_output=True, text=True, timeout=5
        )
        
        return {
            "success": success,
            "service": name,
            "action": action,
            "status": status.stdout.strip(),
            "error": result.stderr if not success else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def control_docker(action: str, name: str) -> dict:
    """Control Docker container"""
    docker_actions = {
        "start": ["docker", "start", name],
        "stop": ["docker", "stop", name],
        "restart": ["docker", "restart", name],
        "remove": ["docker", "rm", "-f", name],
        "logs": ["docker", "logs", "--tail", "50", name]
    }
    
    if action not in docker_actions:
        return {"success": False, "error": f"Invalid action: {action}"}
    
    try:
        result = subprocess.run(
            docker_actions[action],
            capture_output=True, text=True, timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "container": name,
            "action": action,
            "output": result.stdout[:500] if result.stdout else None,
            "error": result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_service_logs(name: str, lines: int = 50) -> dict:
    """Get service logs"""
    try:
        result = subprocess.run(
            ["journalctl", "-u", name, "-n", str(lines), "--no-pager"],
            capture_output=True, text=True, timeout=10
        )
        
        return {
            "service": name,
            "logs": result.stdout.split("\n")[-lines:],
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: service_control.py <action> <name>"}))
        sys.exit(1)
    
    action = sys.argv[1]
    name = sys.argv[2]
    service_type = sys.argv[3] if len(sys.argv) > 3 else "systemd"
    
    if action == "logs":
        result = get_service_logs(name)
    elif service_type == "docker":
        result = control_docker(action, name)
    else:
        result = control_service(action, name)
    
    print(json.dumps(result, indent=2))
