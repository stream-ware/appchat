#!/usr/bin/env python3
"""
Test the shell client itself
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from client.shell_client import StreamwareShellClient, CommandTest


async def test_shell_client():
    """Test shell client functionality"""
    print("🧪 Testing Shell Client...")
    
    tests = [
        CommandTest("start", "system", "welcome"),
        CommandTest("pomoc", "system", "help"),
        CommandTest("pogoda", "internet", "weather"),
        CommandTest("diagnostyka", "diagnostics", "run"),
    ]
    
    async with StreamwareShellClient() as client:
        report = await client.run_tests(tests)
        
        summary = report["summary"]
        print(f"✅ {summary['passed']}/{summary['total']} tests passed")
        
        return summary["failed"] == 0


if __name__ == "__main__":
    success = asyncio.run(test_shell_client())
    sys.exit(0 if success else 1)
