#!/usr/bin/env python3
"""
E2E Tests for Streamware Commands
Tests command parsing, parameter extraction, and app intent recognition
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import logging

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("streamware.e2e_tests")


@dataclass
class CommandTestCase:
    """Test case for command parsing"""
    command: str
    expected_app: str
    expected_action: str
    expected_params: Dict[str, str] = None
    description: str = ""


class E2ECommandTester:
    """
    End-to-end command testing for all Streamware apps
    Tests command recognition, intent mapping, and parameter extraction
    """
    
    def __init__(self):
        # Import after path setup - handle missing dependencies gracefully
        try:
            from backend.main import VoiceCommandProcessor, ViewGenerator
            from backend.data_loader import data_loader
            self.processor = VoiceCommandProcessor
            self.view_generator = ViewGenerator
            self.data_loader = data_loader
        except ImportError as e:
            # Fallback: import only what we need for testing
            logger.warning(f"Full import failed: {e}, using minimal imports")
            from backend.data_loader import data_loader
            self.data_loader = data_loader
            self.processor = None
            self.view_generator = None
        
        self.test_cases = self._build_test_cases()
        self.results = []
    
    def _build_test_cases(self) -> List[CommandTestCase]:
        """Build comprehensive test cases for all apps"""
        return [
            # ===== DOCUMENTS =====
            CommandTestCase("pokaż faktury", "documents", "show_all", description="Show invoices"),
            CommandTestCase("faktury", "documents", "show_all", description="Invoices shortcut"),
            CommandTestCase("zeskanuj fakturę", "documents", "scan_new", description="Scan invoice"),
            CommandTestCase("suma faktur", "documents", "sum_total", description="Sum invoices"),
            CommandTestCase("eksportuj do excel", "documents", "export_excel", description="Export to Excel"),
            
            # ===== CAMERAS =====
            CommandTestCase("pokaż kamery", "cameras", "show_grid", description="Show cameras"),
            CommandTestCase("gdzie ruch", "cameras", "show_motion", description="Motion detection"),
            CommandTestCase("parking", "cameras", "parking", description="Parking camera"),
            
            # ===== SALES =====
            CommandTestCase("pokaż sprzedaż", "sales", "show_dashboard", description="Sales dashboard"),
            CommandTestCase("kpi", "sales", "kpi_dashboard", description="KPI"),
            
            # ===== HOME =====
            CommandTestCase("temperatura", "home", "temperature", description="Temperature"),
            CommandTestCase("oświetlenie", "home", "lighting", description="Lights"),
            CommandTestCase("energia", "home", "energy", description="Energy"),
            
            # ===== ANALYTICS =====
            CommandTestCase("analiza", "analytics", "overview", description="Analytics"),
            CommandTestCase("wykres", "analytics", "chart", description="Chart"),
            
            # ===== INTERNET / WEATHER =====
            CommandTestCase("pogoda", "internet", "weather", description="Weather"),
            CommandTestCase("pogoda kraków", "internet", "weather_krakow", description="Weather Krakow"),
            CommandTestCase("bitcoin", "internet", "crypto", description="Bitcoin"),
            CommandTestCase("kursy walut", "internet", "exchange", description="Currency rates"),
            CommandTestCase("news", "internet", "news", description="News"),
            
            # ===== FILES =====
            CommandTestCase("pokaż pliki", "files", "list", description="Show files"),
            CommandTestCase("moje dokumenty", "files", "documents", description="My documents"),
            CommandTestCase("pobrane", "files", "downloads", description="Downloads"),
            CommandTestCase("znajdź plik", "files", "search", description="Find file"),
            CommandTestCase("ostatnie pliki", "files", "recent", description="Recent files"),
            
            # ===== CLOUD STORAGE =====
            CommandTestCase("połącz onedrive", "cloud_storage", "connect_onedrive", description="Connect OneDrive"),
            CommandTestCase("połącz nextcloud", "cloud_storage", "connect_nextcloud", description="Connect Nextcloud"),
            CommandTestCase("status chmury", "cloud_storage", "cloud_status", description="Cloud status"),
            CommandTestCase("chmura", "cloud_storage", "list_cloud", description="Cloud list"),
            
            # ===== CURLLM =====
            CommandTestCase("zapytaj llm", "curllm", "query", description="Query LLM"),
            CommandTestCase("modele", "curllm", "list_models", description="List models"),
            CommandTestCase("historia llm", "curllm", "history", description="LLM history"),
            CommandTestCase("status llm", "curllm", "status", description="LLM status"),
            CommandTestCase("przetłumacz", "curllm", "translate", description="Translate"),
            CommandTestCase("podsumuj", "curllm", "summarize", description="Summarize"),
            CommandTestCase("kod", "curllm", "code", description="Generate code"),
            
            # ===== SHELL =====
            CommandTestCase("ile pamięci", "shell", "memory", description="Memory usage"),
            CommandTestCase("ile miejsca", "shell", "disk", description="Disk space"),
            
            # ===== DATABASE =====
            CommandTestCase("pokaż tabele", "database", "list_tables", description="Show tables"),
            CommandTestCase("pokaż użytkowników", "database", "list_users", description="Show users"),
            
            # ===== SYSTEM =====
            CommandTestCase("pomoc", "system", "help", description="Help"),
            CommandTestCase("start", "system", "welcome", description="Start"),
            CommandTestCase("status", "system", "status", description="Status"),
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all command tests"""
        logger.info("=" * 60)
        logger.info("🧪 E2E COMMAND TESTS")
        logger.info("=" * 60)
        
        if self.processor is None:
            logger.error("❌ Cannot run tests: VoiceCommandProcessor not available")
            logger.error("   Install dependencies: pip install fastapi uvicorn httpx")
            return {"success": False, "total": 0, "passed": 0, "failed": 0, "error": "Missing dependencies"}
        
        passed = 0
        failed = 0
        failures = []
        
        # Group by app
        apps = {}
        for tc in self.test_cases:
            if tc.expected_app not in apps:
                apps[tc.expected_app] = []
            apps[tc.expected_app].append(tc)
        
        for app_name, test_cases in sorted(apps.items()):
            logger.info(f"\n📱 {app_name.upper()}")
            
            for tc in test_cases:
                result = self._test_command(tc)
                
                if result["passed"]:
                    passed += 1
                    logger.info(f"  ✅ {tc.command[:30]:<30} → {result['actual_app']}/{result['actual_action']}")
                else:
                    failed += 1
                    failures.append(result)
                    logger.info(f"  ❌ {tc.command[:30]:<30} → Expected {tc.expected_app}/{tc.expected_action}, got {result['actual_app']}/{result['actual_action']}")
                
                self.results.append(result)
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 E2E TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"  Total:  {len(self.test_cases)}")
        logger.info(f"  Passed: {passed} ✅")
        logger.info(f"  Failed: {failed} ❌")
        logger.info("=" * 60)
        
        if failures:
            logger.info("\n❌ FAILURES:")
            for f in failures[:10]:
                logger.info(f"  - '{f['command']}' → expected {f['expected_app']}/{f['expected_action']}, got {f['actual_app']}/{f['actual_action']}")
        
        success = failed == 0
        logger.info(f"\n{'🎉 ALL E2E TESTS PASSED!' if success else '❌ SOME E2E TESTS FAILED'}\n")
        
        return {
            "success": success,
            "total": len(self.test_cases),
            "passed": passed,
            "failed": failed,
            "failures": failures
        }
    
    def _test_command(self, tc: CommandTestCase) -> Dict[str, Any]:
        """Test a single command"""
        try:
            result = self.processor.process(tc.command)
            
            actual_app = result.get("app_type", "unknown")
            actual_action = result.get("action", "unknown")
            actual_params = result.get("params", {})
            
            # Check app and action match
            app_match = actual_app == tc.expected_app
            action_match = actual_action == tc.expected_action
            
            # Check params if expected
            params_match = True
            if tc.expected_params:
                for key, value in tc.expected_params.items():
                    if key not in actual_params or actual_params[key].lower() != value.lower():
                        params_match = False
                        break
            
            passed = app_match and action_match and params_match
            
            return {
                "passed": passed,
                "command": tc.command,
                "description": tc.description,
                "expected_app": tc.expected_app,
                "expected_action": tc.expected_action,
                "expected_params": tc.expected_params,
                "actual_app": actual_app,
                "actual_action": actual_action,
                "actual_params": actual_params,
                "app_match": app_match,
                "action_match": action_match,
                "params_match": params_match
            }
            
        except Exception as e:
            return {
                "passed": False,
                "command": tc.command,
                "description": tc.description,
                "expected_app": tc.expected_app,
                "expected_action": tc.expected_action,
                "actual_app": "ERROR",
                "actual_action": str(e),
                "error": str(e)
            }
    
    def test_view_generation(self) -> Dict[str, Any]:
        """Test that views are generated correctly for each app"""
        logger.info("\n" + "=" * 60)
        logger.info("🎨 VIEW GENERATION TESTS")
        logger.info("=" * 60)
        
        apps_to_test = [
            ("documents", "show_all"),
            ("cameras", "show_all"),
            ("sales", "dashboard"),
            ("home", "temperature"),
            ("analytics", "dashboard"),
            ("internet", "weather"),
            ("system", "help"),
            ("system", "welcome"),
            ("files", "list"),
            ("cloud_storage", "list"),
            ("curllm", "status"),
            ("monitoring", "overview"),
            ("services", "list"),
        ]
        
        passed = 0
        failed = 0
        
        for app_type, action in apps_to_test:
            try:
                view = self.view_generator.generate(app_type, action)
                
                if view and view.get("type"):
                    passed += 1
                    logger.info(f"  ✅ {app_type}/{action} → {view.get('title', 'No title')[:40]}")
                else:
                    failed += 1
                    logger.info(f"  ❌ {app_type}/{action} → Empty view")
            except Exception as e:
                failed += 1
                logger.info(f"  ❌ {app_type}/{action} → Error: {str(e)[:50]}")
        
        logger.info(f"\n  View tests: {passed}/{passed+failed} passed")
        
        return {"passed": passed, "failed": failed}
    
    def save_report(self, filepath: str = "tests/e2e_report.json"):
        """Save test report"""
        report = {
            "total": len(self.results),
            "passed": sum(1 for r in self.results if r["passed"]),
            "failed": sum(1 for r in self.results if not r["passed"]),
            "results": self.results
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Report saved to: {filepath}")


def main():
    """Run E2E tests"""
    tester = E2ECommandTester()
    
    # Run command tests
    cmd_results = tester.run_all_tests()
    
    # Run view tests
    view_results = tester.test_view_generation()
    
    # Save report
    tester.save_report()
    
    # Exit code
    sys.exit(0 if cmd_results["success"] else 1)


if __name__ == "__main__":
    main()
