#!/usr/bin/env python3
"""
Streamware E2E Test - Global command testing
Tests all user commands via VoiceCommandProcessor and ViewGenerator
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import VoiceCommandProcessor, ViewGenerator, app_registry
from backend.makefile_converter import makefile_converter

# Test categories
TEST_COMMANDS = {
    "documents": [
        "pokaż faktury",
        "dokumenty", 
        "suma faktur",
        "faktury do zapłaty",
    ],
    "cameras": [
        "pokaż kamery",
        "monitoring",
        "alerty",
    ],
    "sales": [
        "pokaż sprzedaż",
        "raport",
        "top produkty",
    ],
    "home": [
        "temperatura",
        "oświetlenie",
        "alarm",
    ],
    "analytics": [
        "analiza",
        "wykres",
        "anomalie",
    ],
    "internet": [
        "pogoda",
        "bitcoin",
        "rss",
        "integracje",
    ],
    "system": [
        "pomoc",
        "status",
        "start",
    ],
    # Modular apps
    "services": [
        "usługi",
        "docker",
    ],
    "monitoring": [
        "cpu",
        "pamięć",
        "dysk",
    ],
    "backup": [
        "backup",
        "lista kopii",
    ],
}

class E2ETestRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "categories": {}
        }
    
    def test_command(self, command: str) -> dict:
        """Test a single command"""
        try:
            # Process command
            intent = VoiceCommandProcessor.process(command)
            
            if not intent.get("recognized"):
                return {
                    "success": False,
                    "error": "Command not recognized",
                    "intent": intent
                }
            
            # Generate view (sync version for testing)
            view = ViewGenerator.generate(intent["app_type"], intent["action"])
            
            return {
                "success": True,
                "intent": intent,
                "view_type": view.get("type"),
                "view_title": view.get("title", "N/A")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_async_command(self, command: str) -> dict:
        """Test async command (internet/weather)"""
        try:
            intent = VoiceCommandProcessor.process(command)
            
            if not intent.get("recognized"):
                return {"success": False, "error": "Not recognized"}
            
            if intent["app_type"] == "internet":
                view = await ViewGenerator.generate_async(intent["app_type"], intent["action"])
            else:
                view = ViewGenerator.generate(intent["app_type"], intent["action"])
            
            # Check if view has actual data (not just loading)
            has_data = view.get("data") or view.get("stats") or view.get("title")
            
            return {
                "success": True,
                "intent": intent,
                "view_type": view.get("type"),
                "view_title": view.get("title", "N/A"),
                "has_data": has_data
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_text2makefile(self, text: str, app_id: str = None) -> dict:
        """Test text2makefile conversion"""
        try:
            result = makefile_converter.text2makefile(text, app_id)
            return {
                "success": result.get("success", False),
                "command": result.get("command"),
                "error": result.get("error")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_all_tests(self, verbose: bool = True):
        """Run all E2E tests"""
        print("=" * 60)
        print("🧪 STREAMWARE E2E TEST")
        print("=" * 60)
        print()
        
        # Load apps
        app_registry.scan_apps()
        print(f"📦 Apps loaded: {len(app_registry.apps)}")
        print()
        
        for category, commands in TEST_COMMANDS.items():
            print(f"📁 Testing: {category.upper()}")
            self.results["categories"][category] = {"passed": 0, "failed": 0, "tests": []}
            
            for cmd in commands:
                self.results["total"] += 1
                
                # Use async for internet commands
                if category == "internet":
                    result = await self.test_async_command(cmd)
                else:
                    result = self.test_command(cmd)
                
                test_result = {
                    "command": cmd,
                    "success": result["success"],
                    "details": result
                }
                
                if result["success"]:
                    self.results["passed"] += 1
                    self.results["categories"][category]["passed"] += 1
                    status = "✅"
                else:
                    self.results["failed"] += 1
                    self.results["categories"][category]["failed"] += 1
                    self.results["errors"].append({"command": cmd, "error": result.get("error")})
                    status = "❌"
                
                self.results["categories"][category]["tests"].append(test_result)
                
                if verbose:
                    view_info = result.get("view_title", result.get("error", ""))[:40]
                    print(f"  {status} '{cmd}' → {view_info}")
            
            print()
        
        # Test text2makefile
        print("📁 Testing: TEXT2MAKEFILE")
        t2m_tests = [
            ("pokaż pogodę", "weather"),
            ("ustaw timeout 30", "weather"),
            ("pokaż usługi", "services"),
        ]
        
        for text, app_id in t2m_tests:
            self.results["total"] += 1
            result = self.test_text2makefile(text, app_id)
            
            if result["success"]:
                self.results["passed"] += 1
                print(f"  ✅ '{text}' → {result.get('command', 'N/A')}")
            else:
                self.results["failed"] += 1
                print(f"  ❌ '{text}' → {result.get('error', 'Unknown')}")
        
        print()
        
        # Summary
        print("=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"  Total:  {self.results['total']}")
        print(f"  Passed: {self.results['passed']} ✅")
        print(f"  Failed: {self.results['failed']} ❌")
        print(f"  Rate:   {self.results['passed']/self.results['total']*100:.1f}%")
        print()
        
        if self.results["errors"]:
            print("❌ ERRORS:")
            for err in self.results["errors"][:10]:
                print(f"  - {err['command']}: {err['error']}")
        
        # Save results
        results_file = Path(__file__).parent.parent / "data" / "e2e_results.json"
        results_file.parent.mkdir(exist_ok=True)
        results_file.write_text(json.dumps(self.results, indent=2, default=str))
        print(f"\n📄 Results saved to: {results_file}")
        
        return self.results["failed"] == 0

async def main():
    runner = E2ETestRunner()
    success = await runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
