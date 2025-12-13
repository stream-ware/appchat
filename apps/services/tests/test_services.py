#!/usr/bin/env python3
"""Services App Tests"""
import sys
import json
sys.path.insert(0, str(__file__).replace('/tests/test_services.py', '/scripts'))

def test_list_services():
    from list_services import get_systemd_services
    result = get_systemd_services()
    assert isinstance(result, list)
    print("✅ List services test passed")
    return True

def test_docker_containers():
    from list_services import get_docker_containers
    result = get_docker_containers()
    assert isinstance(result, list)
    print("✅ Docker containers test passed")
    return True

if __name__ == "__main__":
    tests = [test_list_services, test_docker_containers]
    passed = sum(1 for t in tests if t())
    print(f"\nTests: {passed}/{len(tests)} passed")
    print(json.dumps({"passed": passed, "total": len(tests)}))
