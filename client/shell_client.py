#!/usr/bin/env python3
"""
Streamware Shell Client
Automated testing client for simulating GUI interactions via commands
"""

import asyncio
import aiohttp
import json
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("streamware.client")


@dataclass
class CommandTest:
    """Single command test case"""
    command: str
    expected_app_type: Optional[str] = None
    expected_action: Optional[str] = None
    expected_keywords: List[str] = None
    timeout: int = 10
    should_succeed: bool = True


@dataclass
class TestResult:
    """Result of a command test"""
    command: str
    success: bool
    response_time: float
    app_type: Optional[str] = None
    action: Optional[str] = None
    error: Optional[str] = None
    response_data: Optional[Dict] = None


class StreamwareShellClient:
    """Shell client for testing Streamware commands"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.results: List[TestResult] = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_command(self, command: str) -> Dict[str, Any]:
        """Send command to backend via WebSocket simulation"""
        if not self.session:
            raise RuntimeError("Client not initialized - use async with")
        
        start_time = datetime.now()
        
        try:
            # Use command endpoint to simulate WebSocket command
            async with self.session.post(
                f"{self.base_url}/api/command/send",
                json={"command": command},
                timeout=10
            ) as resp:
                response_time = (datetime.now() - start_time).total_seconds()
                
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "success": True,
                        "data": data,
                        "response_time": response_time
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status}: {await resp.text()}",
                        "response_time": response_time
                    }
        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Timeout",
                "response_time": (datetime.now() - start_time).total_seconds()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def test_command(self, test: CommandTest) -> TestResult:
        """Test a single command"""
        logger.info(f"🧪 Testing: {test.command}")
        
        result = await self.send_command(test.command)
        
        # Extract data from response
        app_type = None
        action = None
        response_data = None
        
        if result["success"] and result["data"]:
            data = result["data"]
            response_data = data
            
            # Extract from view data if available
            if "view" in data:
                app_type = data["view"].get("type")
                action = data["view"].get("action")
            
            # Extract from recognition if available
            if "recognized" in data:
                app_type = data.get("app_type")
                action = data.get("action")
        
        # Validate expectations
        success = result["success"]
        error = result["error"] if not result["success"] else None
        
        if success and test.expected_app_type and app_type != test.expected_app_type:
            success = False
            error = f"Expected app_type {test.expected_app_type}, got {app_type}"
        
        if success and test.expected_action and action != test.expected_action:
            success = False
            error = f"Expected action {test.expected_action}, got {action}"
        
        if success and test.expected_keywords:
            response_text = json.dumps(response_data or {}).lower()
            for keyword in test.expected_keywords:
                if keyword.lower() not in response_text:
                    success = False
                    error = f"Expected keyword '{keyword}' not found in response"
                    break
        
        test_result = TestResult(
            command=test.command,
            success=success == test.should_succeed,
            response_time=result["response_time"],
            app_type=app_type,
            action=action,
            error=error,
            response_data=response_data
        )
        
        self.results.append(test_result)
        
        # Log result
        status = "✅" if test_result.success else "❌"
        logger.info(f"   {status} {app_type}/{action} ({result['response_time']:.2f}s)")
        if error:
            logger.info(f"      → {error}")
        
        return test_result
    
    async def run_tests(self, tests: List[CommandTest]) -> Dict[str, Any]:
        """Run multiple tests"""
        logger.info("=" * 60)
        logger.info("🧪 STREAMWARE COMMAND TESTS")
        logger.info("=" * 60)
        
        self.results = []
        
        for test in tests:
            await self.test_command(test)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        
        avg_response = sum(r.response_time for r in self.results) / total if total > 0 else 0
        
        # Group by app type
        by_app = {}
        for result in self.results:
            app = result.app_type or "unknown"
            if app not in by_app:
                by_app[app] = {"total": 0, "passed": 0, "failed": 0, "avg_time": 0}
            by_app[app]["total"] += 1
            if result.success:
                by_app[app]["passed"] += 1
            else:
                by_app[app]["failed"] += 1
            by_app[app]["avg_time"] += result.response_time
        
        # Calculate averages
        for app in by_app:
            by_app[app]["avg_time"] /= by_app[app]["total"]
        
        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": round(passed / total * 100, 1) if total > 0 else 0,
                "avg_response_time": round(avg_response, 3)
            },
            "by_app": by_app,
            "results": [
                {
                    "command": r.command,
                    "success": r.success,
                    "app_type": r.app_type,
                    "action": r.action,
                    "response_time": r.response_time,
                    "error": r.error
                }
                for r in self.results
            ]
        }


# Predefined test suites
BASIC_TESTS = [
    CommandTest("start", "system", "welcome"),
    CommandTest("pomoc", "system", "help"),
    CommandTest("pokaż faktury", "documents", "show_all"),
    CommandTest("pokaż kamery", "cameras", "show_grid"),
    CommandTest("pokaż sprzedaż", "sales", "show_dashboard"),
    CommandTest("pogoda", "internet", "weather"),
    CommandTest("kursy walut", "internet", "exchange"),
    CommandTest("rejestry", "registry", "show_all"),
    CommandTest("pokaż pliki", "files", "list"),
    CommandTest("chmura", "cloud_storage", "list_cloud"),
    CommandTest("status llm", "curllm", "status"),
    CommandTest("diagnostyka", "diagnostics", "run"),
]

INTERNET_TESTS = [
    CommandTest("pogoda", "internet", "weather", ["weather", "temperature"]),
    CommandTest("pogoda kraków", "internet", "weather", ["kraków"]),
    CommandTest("kursy walut", "internet", "exchange", ["eur", "usd", "pln"]),
    CommandTest("bitcoin", "internet", "crypto", ["bitcoin", "btc"]),
    CommandTest("rss", "internet", "rss", ["feed", "news"]),
]

CLOUD_TESTS = [
    CommandTest("chmura", "cloud_storage", "list_cloud", ["cloud", "storage"]),
    CommandTest("połącz onedrive", "cloud_storage", "connect_onedrive", ["onedrive", "form"]),
    CommandTest("połącz nextcloud", "cloud_storage", "connect_nextcloud", ["nextcloud", "form"]),
    CommandTest("połącz google drive", "cloud_storage", "connect_gdrive", ["google", "drive"]),
]

FILES_TESTS = [
    CommandTest("pokaż pliki", "files", "list", ["files", "documents"]),
    CommandTest("moje dokumenty", "files", "documents", ["documents"]),
    CommandTest("pobrane", "files", "downloads", ["downloads"]),
    CommandTest("znajdź plik", "files", "search", ["search"]),
]

DIAGNOSTIC_TESTS = [
    CommandTest("diagnostyka", "diagnostics", "run", ["health", "score"]),
    CommandTest("sprawdź system", "diagnostics", "run", ["diagnostic"]),
    CommandTest("co działa", "diagnostics", "run", ["functional"]),
]

ALL_TEST_SUITES = {
    "basic": BASIC_TESTS,
    "internet": INTERNET_TESTS,
    "cloud": CLOUD_TESTS,
    "files": FILES_TESTS,
    "diagnostic": DIAGNOSTIC_TESTS,
    "all": BASIC_TESTS + INTERNET_TESTS + CLOUD_TESTS + FILES_TESTS + DIAGNOSTIC_TESTS,
}


async def run_tests(suite: str = "all", base_url: str = "http://localhost:8001"):
    """Run test suite"""
    if suite not in ALL_TEST_SUITES:
        print(f"❌ Unknown test suite: {suite}")
        print(f"Available: {', '.join(ALL_TEST_SUITES.keys())}")
        return 1
    
    tests = ALL_TEST_SUITES[suite]
    
    async with StreamwareShellClient(base_url) as client:
        report = await client.run_tests(tests)
        
        # Print summary
        summary = report["summary"]
        print()
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total:   {summary['total']}")
        print(f"Passed:  {summary['passed']} ✅")
        print(f"Failed:  {summary['failed']} ❌")
        print(f"Success: {summary['success_rate']}%")
        print(f"Avg Time: {summary['avg_response_time']}s")
        
        # Print by app
        print()
        print("📊 BY APP:")
        for app, stats in report["by_app"].items():
            success_rate = round(stats["passed"] / stats["total"] * 100, 1)
            print(f"  {app}: {stats['passed']}/{stats['total']} ({success_rate}%) - {stats['avg_time']:.3f}s avg")
        
        # Print failures
        failures = [r for r in report["results"] if not r["success"]]
        if failures:
            print()
            print("❌ FAILURES:")
            for failure in failures:
                print(f"  {failure['command']}: {failure['error']}")
        
        # Save report
        report_file = Path("test_report.json")
        report_file.write_text(json.dumps(report, indent=2))
        print(f"\n📄 Report saved to: {report_file}")
        
        return 0 if summary["failed"] == 0 else 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Streamware Shell Client")
    parser.add_argument("command", nargs="?", help="Single command to test")
    parser.add_argument("--suite", "-s", default="basic", choices=ALL_TEST_SUITES.keys(), help="Test suite to run")
    parser.add_argument("--url", "-u", default="http://localhost:8001", help="Base URL")
    parser.add_argument("--list-suites", action="store_true", help="List available test suites")
    
    args = parser.parse_args()
    
    if args.list_suites:
        print("Available test suites:")
        for name, tests in ALL_TEST_SUITES.items():
            print(f"  {name}: {len(tests)} tests")
        return 0
    
    if args.command:
        # Single command test
        async def test_single():
            async with StreamwareShellClient(args.url) as client:
                result = await client.send_command(args.command)
                print(json.dumps(result, indent=2))
                return 0 if result["success"] else 1
        
        return asyncio.run(test_single())
    else:
        # Run test suite
        return asyncio.run(run_tests(args.suite, args.url))


if __name__ == "__main__":
    sys.exit(main())
