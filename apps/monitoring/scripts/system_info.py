#!/usr/bin/env python3
"""System monitoring - CPU, RAM, Disk, Network"""

import subprocess
import json
import sys
import os

def get_cpu_info():
    """Get CPU usage and info"""
    try:
        # CPU usage
        load = os.getloadavg()
        
        # CPU count
        cpu_count = os.cpu_count() or 1
        
        # Top processes by CPU
        top = subprocess.run(
            ["ps", "-eo", "pid,comm,%cpu", "--sort=-%cpu"],
            capture_output=True, text=True, timeout=5
        )
        top_procs = []
        for line in top.stdout.strip().split("\n")[1:6]:
            parts = line.split()
            if len(parts) >= 3:
                top_procs.append({"pid": parts[0], "name": parts[1], "cpu": parts[2]})
        
        return {
            "load_1m": load[0],
            "load_5m": load[1],
            "load_15m": load[2],
            "cores": cpu_count,
            "usage_percent": round(load[0] / cpu_count * 100, 1),
            "top_processes": top_procs
        }
    except Exception as e:
        return {"error": str(e)}

def get_memory_info():
    """Get RAM usage"""
    try:
        with open("/proc/meminfo") as f:
            meminfo = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    meminfo[parts[0].rstrip(":")] = int(parts[1])
        
        total = meminfo.get("MemTotal", 0) / 1024  # MB
        free = meminfo.get("MemAvailable", meminfo.get("MemFree", 0)) / 1024
        used = total - free
        
        return {
            "total_mb": round(total),
            "used_mb": round(used),
            "free_mb": round(free),
            "usage_percent": round(used / total * 100, 1) if total > 0 else 0
        }
    except Exception as e:
        return {"error": str(e)}

def get_disk_info():
    """Get disk usage"""
    try:
        result = subprocess.run(
            ["df", "-h", "--output=source,size,used,avail,pcent,target"],
            capture_output=True, text=True, timeout=5
        )
        
        disks = []
        for line in result.stdout.strip().split("\n")[1:]:
            parts = line.split()
            if len(parts) >= 6 and not parts[0].startswith("tmpfs"):
                disks.append({
                    "device": parts[0],
                    "size": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "usage_percent": parts[4],
                    "mount": parts[5]
                })
        
        return {"disks": disks}
    except Exception as e:
        return {"error": str(e)}

def get_network_info():
    """Get network stats"""
    try:
        result = subprocess.run(
            ["ip", "-s", "link"],
            capture_output=True, text=True, timeout=5
        )
        
        interfaces = []
        current = None
        
        for line in result.stdout.strip().split("\n"):
            if ": " in line and not line.startswith(" "):
                parts = line.split(": ")
                if len(parts) >= 2:
                    if current:
                        interfaces.append(current)
                    current = {"name": parts[1].split("@")[0], "rx_bytes": 0, "tx_bytes": 0}
            elif current and "RX:" in line:
                pass  # Header
            elif current and line.strip().startswith("RX:"):
                pass
            elif current and "bytes" in line.lower():
                parts = line.split()
                if len(parts) >= 1:
                    try:
                        current["rx_bytes"] = int(parts[0])
                    except:
                        pass
        
        if current:
            interfaces.append(current)
        
        return {"interfaces": interfaces[:5]}  # Limit
    except Exception as e:
        return {"error": str(e)}

def get_processes():
    """Get top processes"""
    try:
        result = subprocess.run(
            ["ps", "-eo", "pid,user,comm,%mem,%cpu", "--sort=-%mem"],
            capture_output=True, text=True, timeout=5
        )
        
        processes = []
        for line in result.stdout.strip().split("\n")[1:11]:
            parts = line.split()
            if len(parts) >= 5:
                processes.append({
                    "pid": parts[0],
                    "user": parts[1],
                    "name": parts[2],
                    "mem": parts[3],
                    "cpu": parts[4]
                })
        
        return {"processes": processes}
    except Exception as e:
        return {"error": str(e)}

def get_overview():
    """Get system overview"""
    return {
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "uptime": subprocess.run(["uptime", "-p"], capture_output=True, text=True).stdout.strip()
    }

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "overview"
    
    commands = {
        "overview": get_overview,
        "cpu": get_cpu_info,
        "memory": get_memory_info,
        "disk": get_disk_info,
        "network": get_network_info,
        "processes": get_processes
    }
    
    result = commands.get(cmd, get_overview)()
    print(json.dumps(result, indent=2))
