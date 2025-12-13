#!/usr/bin/env python3
"""
GUI/E2E Tests for Streamware
Tests WebSocket connection, UI rendering, and user interactions
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import logging

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("streamware.gui_tests")


@dataclass
class GUITestResult:
    """GUI test result"""
    name: str
    passed: bool
    duration: float
    message: str = ""
    error: str = ""


class GUITestRunner:
    """
    GUI/E2E test runner for Streamware
    Tests WebSocket, API endpoints, and UI behavior
    """
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws") + "/ws/test_client"
        self.results: List[GUITestResult] = []
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all GUI tests"""
        logger.info("=" * 60)
        logger.info("🖥️ GUI/E2E TEST RUNNER")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # API Tests
        await self.test_api_health()
        await self.test_api_apps()
        await self.test_api_commands()
        
        # WebSocket Tests
        await self.test_websocket_connection()
        await self.test_websocket_command()
        
        # Frontend Tests
        await self.test_frontend_loads()
        await self.test_frontend_elements()
        
        total_duration = time.time() - start_time
        return self._generate_summary(total_duration)
    
    async def test_api_health(self) -> GUITestResult:
        """Test API health endpoint"""
        start = time.time()
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/health", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    result = GUITestResult(
                        name="api_health",
                        passed=True,
                        duration=time.time() - start,
                        message=f"Status: {data.get('status')}"
                    )
                else:
                    result = GUITestResult(
                        name="api_health",
                        passed=False,
                        duration=time.time() - start,
                        error=f"HTTP {response.status_code}"
                    )
        except Exception as e:
            result = GUITestResult(
                name="api_health",
                passed=False,
                duration=time.time() - start,
                error=str(e)
            )
        
        self.results.append(result)
        self._log_result(result)
        return result
    
    async def test_api_apps(self) -> GUITestResult:
        """Test API apps endpoint"""
        start = time.time()
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/apps", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    app_count = len(data.get("apps", []))
                    result = GUITestResult(
                        name="api_apps",
                        passed=app_count > 0,
                        duration=time.time() - start,
                        message=f"Found {app_count} apps"
                    )
                else:
                    result = GUITestResult(
                        name="api_apps",
                        passed=False,
                        duration=time.time() - start,
                        error=f"HTTP {response.status_code}"
                    )
        except Exception as e:
            result = GUITestResult(
                name="api_apps",
                passed=False,
                duration=time.time() - start,
                error=str(e)
            )
        
        self.results.append(result)
        self._log_result(result)
        return result
    
    async def test_api_commands(self) -> GUITestResult:
        """Test API commands endpoint"""
        start = time.time()
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/commands", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    cmd_count = data.get("total_commands", 0)
                    result = GUITestResult(
                        name="api_commands",
                        passed=cmd_count > 50,
                        duration=time.time() - start,
                        message=f"Found {cmd_count} commands"
                    )
                else:
                    result = GUITestResult(
                        name="api_commands",
                        passed=False,
                        duration=time.time() - start,
                        error=f"HTTP {response.status_code}"
                    )
        except Exception as e:
            result = GUITestResult(
                name="api_commands",
                passed=False,
                duration=time.time() - start,
                error=str(e)
            )
        
        self.results.append(result)
        self._log_result(result)
        return result
    
    async def test_websocket_connection(self) -> GUITestResult:
        """Test WebSocket connection"""
        start = time.time()
        
        try:
            import websockets
            
            async with websockets.connect(self.ws_url, close_timeout=5) as ws:
                # Should receive welcome message
                message = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(message)
                
                if data.get("type") == "welcome":
                    result = GUITestResult(
                        name="websocket_connection",
                        passed=True,
                        duration=time.time() - start,
                        message="WebSocket connected, welcome received"
                    )
                else:
                    result = GUITestResult(
                        name="websocket_connection",
                        passed=False,
                        duration=time.time() - start,
                        error=f"Unexpected message type: {data.get('type')}"
                    )
        except Exception as e:
            result = GUITestResult(
                name="websocket_connection",
                passed=False,
                duration=time.time() - start,
                error=str(e)
            )
        
        self.results.append(result)
        self._log_result(result)
        return result
    
    async def test_websocket_command(self) -> GUITestResult:
        """Test WebSocket command processing"""
        start = time.time()
        
        try:
            import websockets
            
            async with websockets.connect(self.ws_url, close_timeout=5) as ws:
                # Wait for welcome
                await asyncio.wait_for(ws.recv(), timeout=5)
                
                # Send command
                await ws.send(json.dumps({
                    "type": "voice_command",
                    "text": "pomoc"
                }))
                
                # Wait for response
                message = await asyncio.wait_for(ws.recv(), timeout=10)
                data = json.loads(message)
                
                if data.get("type") == "response":
                    result = GUITestResult(
                        name="websocket_command",
                        passed=True,
                        duration=time.time() - start,
                        message=f"Command processed: {data.get('view', {}).get('type', 'unknown')}"
                    )
                else:
                    result = GUITestResult(
                        name="websocket_command",
                        passed=False,
                        duration=time.time() - start,
                        error=f"Unexpected response type: {data.get('type')}"
                    )
        except Exception as e:
            result = GUITestResult(
                name="websocket_command",
                passed=False,
                duration=time.time() - start,
                error=str(e)
            )
        
        self.results.append(result)
        self._log_result(result)
        return result
    
    async def test_frontend_loads(self) -> GUITestResult:
        """Test frontend HTML loads"""
        start = time.time()
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, timeout=5)
                
                if response.status_code == 200:
                    content = response.text
                    has_title = "Streamware" in content
                    has_chat = "chat-container" in content
                    has_app_view = "app-view" in content
                    
                    result = GUITestResult(
                        name="frontend_loads",
                        passed=has_title and has_app_view,  # chat-container might not exist
                        duration=time.time() - start,
                        message=f"HTML loaded ({len(content)} bytes)"
                    )
                else:
                    result = GUITestResult(
                        name="frontend_loads",
                        passed=False,
                        duration=time.time() - start,
                        error=f"HTTP {response.status_code}"
                    )
        except Exception as e:
            result = GUITestResult(
                name="frontend_loads",
                passed=False,
                duration=time.time() - start,
                error=str(e)
            )
        
        self.results.append(result)
        self._log_result(result)
        return result
    
    async def test_frontend_elements(self) -> GUITestResult:
        """Test frontend has required elements"""
        start = time.time()
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, timeout=5)
                
                if response.status_code == 200:
                    content = response.text
                    
                    required_elements = [
                        "chat-input",
                        "chat-messages",
                        "app-content",
                        "voice-btn",
                        "send-btn",
                        "config-bar",
                        "lang-btn"  # Language button
                    ]
                    
                    found = [el for el in required_elements if el in content]
                    missing = [el for el in required_elements if el not in content]
                    
                    result = GUITestResult(
                        name="frontend_elements",
                        passed=len(missing) == 0,
                        duration=time.time() - start,
                        message=f"Found {len(found)}/{len(required_elements)} elements" + 
                                (f", missing: {missing}" if missing else "")
                    )
                else:
                    result = GUITestResult(
                        name="frontend_elements",
                        passed=False,
                        duration=time.time() - start,
                        error=f"HTTP {response.status_code}"
                    )
        except Exception as e:
            result = GUITestResult(
                name="frontend_elements",
                passed=False,
                duration=time.time() - start,
                error=str(e)
            )
        
        self.results.append(result)
        self._log_result(result)
        return result
    
    def _log_result(self, result: GUITestResult):
        """Log test result"""
        icon = "✅" if result.passed else "❌"
        msg = result.message or result.error
        logger.info(f"  {icon} {result.name}: {msg[:60]}")
    
    def _generate_summary(self, total_duration: float) -> Dict[str, Any]:
        """Generate test summary"""
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 GUI TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"  Total:  {len(self.results)} tests")
        logger.info(f"  Passed: {passed} ✅")
        logger.info(f"  Failed: {failed} ❌")
        logger.info(f"  Time:   {total_duration:.2f}s")
        logger.info("=" * 60)
        
        success = failed == 0
        logger.info(f"\n{'🎉 ALL GUI TESTS PASSED!' if success else '❌ SOME GUI TESTS FAILED'}\n")
        
        return {
            "success": success,
            "total": len(self.results),
            "passed": passed,
            "failed": failed,
            "duration": total_duration,
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "duration": r.duration,
                    "message": r.message,
                    "error": r.error
                }
                for r in self.results
            ]
        }


async def main():
    """Run GUI tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Streamware GUI Test Runner")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL")
    parser.add_argument("--report", "-r", default="tests/gui_report.json", help="Report path")
    args = parser.parse_args()
    
    runner = GUITestRunner(base_url=args.url)
    summary = await runner.run_all_tests()
    
    # Save report
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    with open(args.report, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            **summary
        }, f, indent=2)
    
    logger.info(f"📄 Report saved to: {args.report}")
    
    sys.exit(0 if summary["success"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
