#!/usr/bin/env python3
"""List and analyze system services"""

import subprocess
import json
import sys
from typing import List, Dict

def get_systemd_services() -> List[Dict]:
    """Get systemd services status"""
    try:
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--all", "--no-pager", "--plain"],
            capture_output=True, text=True, timeout=10
        )
        
        services = []
        for line in result.stdout.strip().split("\n")[1:]:
            parts = line.split()
            if len(parts) >= 4:
                services.append({
                    "name": parts[0].replace(".service", ""),
                    "load": parts[1],
                    "active": parts[2],
                    "sub": parts[3],
                    "type": "systemd"
                })
        return services
    except Exception as e:
        return [{"error": str(e)}]

def get_docker_containers() -> List[Dict]:
    """Get Docker containers status"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{json .}}"],
            capture_output=True, text=True, timeout=10
        )
        
        containers = []
        for line in result.stdout.strip().split("\n"):
            if line:
                try:
                    data = json.loads(line)
                    containers.append({
                        "name": data.get("Names", ""),
                        "image": data.get("Image", ""),
                        "status": data.get("Status", ""),
                        "state": data.get("State", ""),
                        "ports": data.get("Ports", ""),
                        "type": "docker"
                    })
                except json.JSONDecodeError:
                    pass
        return containers
    except FileNotFoundError:
        return []
    except Exception as e:
        return [{"error": str(e)}]

def get_service_status(name: str) -> Dict:
    """Get detailed status of a service"""
    try:
        # Try systemd first
        result = subprocess.run(
            ["systemctl", "status", name, "--no-pager"],
            capture_output=True, text=True, timeout=10
        )
        
        is_active = subprocess.run(
            ["systemctl", "is-active", name],
            capture_output=True, text=True, timeout=5
        )
        
        return {
            "name": name,
            "active": is_active.stdout.strip() == "active",
            "status": is_active.stdout.strip(),
            "details": result.stdout[:500],
            "type": "systemd"
        }
    except Exception as e:
        return {"name": name, "error": str(e)}

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if cmd == "systemd":
        print(json.dumps({"services": get_systemd_services()}, indent=2))
    elif cmd == "docker":
        print(json.dumps({"containers": get_docker_containers()}, indent=2))
    elif cmd == "status" and len(sys.argv) > 2:
        print(json.dumps(get_service_status(sys.argv[2]), indent=2))
    else:
        # All services
        result = {
            "systemd": get_systemd_services()[:20],  # Limit
            "docker": get_docker_containers()
        }
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
