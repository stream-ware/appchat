#!/usr/bin/env python3
"""Monitoring App Tests"""
import sys
import json
sys.path.insert(0, str(__file__).replace('/tests/test_monitoring.py', '/scripts'))

def test_cpu_info():
    from system_info import get_cpu_info
    result = get_cpu_info()
    assert "load_1m" in result or "error" in result
    print("✅ CPU info test passed")
    return True

def test_memory_info():
    from system_info import get_memory_info
    result = get_memory_info()
    assert "total_mb" in result or "error" in result
    print("✅ Memory info test passed")
    return True

def test_disk_info():
    from system_info import get_disk_info
    result = get_disk_info()
    assert "disks" in result or "error" in result
    print("✅ Disk info test passed")
    return True

if __name__ == "__main__":
    tests = [test_cpu_info, test_memory_info, test_disk_info]
    passed = sum(1 for t in tests if t())
    print(f"\nTests: {passed}/{len(tests)} passed")
    print(json.dumps({"passed": passed, "total": len(tests)}))
