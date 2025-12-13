"""
Automated View Rendering Tests
Tests that all views render correctly without undefined/null values
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("streamware.view_tests")


@dataclass
class ViewTestResult:
    app_type: str
    action: str
    success: bool
    errors: List[str]


class ViewRenderingTester:
    """Tests that all views render correctly without undefined values"""
    
    def __init__(self):
        try:
            from backend.main import ViewGenerator, VoiceCommandProcessor
            self.view_generator = ViewGenerator
            self.processor = VoiceCommandProcessor
        except ImportError as e:
            logger.error(f"Failed to import: {e}")
            self.view_generator = None
            self.processor = None
        
        self.results: List[ViewTestResult] = []
    
    def validate_view(self, view: Dict[str, Any], path: str = "") -> List[str]:
        """Recursively validate view data for undefined/null values"""
        errors = []
        
        if view is None:
            errors.append(f"{path}: view is None")
            return errors
        
        for key, value in view.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check for None/undefined
            if value is None and key not in ['last_sync', 'last_update', 'data']:
                errors.append(f"{current_path}: value is None")
            
            # Check for "undefined" string (JS artifact)
            if isinstance(value, str) and 'undefined' in value.lower():
                errors.append(f"{current_path}: contains 'undefined'")
            
            # Recursively check dicts
            if isinstance(value, dict):
                errors.extend(self.validate_view(value, current_path))
            
            # Check lists
            if isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        errors.extend(self.validate_view(item, f"{current_path}[{i}]"))
                    elif item is None:
                        errors.append(f"{current_path}[{i}]: item is None")
        
        return errors
    
    def validate_actions(self, view: Dict[str, Any]) -> List[str]:
        """Validate that action buttons have required fields"""
        errors = []
        
        for key in ['actions', 'quick_actions']:
            actions = view.get(key, [])
            for i, action in enumerate(actions):
                if isinstance(action, dict):
                    # Check for label
                    if not action.get('label') and not action.get('id'):
                        errors.append(f"{key}[{i}]: missing label and id")
                    
                    # Check for cmd or id (one should exist)
                    if not action.get('cmd') and not action.get('id'):
                        errors.append(f"{key}[{i}]: missing cmd and id")
        
        return errors
    
    def validate_stats(self, view: Dict[str, Any]) -> List[str]:
        """Validate stats have required fields"""
        errors = []
        
        stats = view.get('stats', [])
        for i, stat in enumerate(stats):
            if isinstance(stat, dict):
                if not stat.get('label'):
                    errors.append(f"stats[{i}]: missing label")
                if stat.get('value') is None:
                    errors.append(f"stats[{i}]: value is None")
        
        return errors
    
    def test_view(self, app_type: str, action: str) -> ViewTestResult:
        """Test a single view"""
        errors = []
        
        try:
            view = self.view_generator.generate(app_type, action)
            
            # Basic validation
            if not view:
                errors.append("View is empty/None")
            else:
                # Check required fields
                if not view.get('type'):
                    errors.append("Missing 'type' field")
                if not view.get('title'):
                    errors.append("Missing 'title' field")
                
                # Validate for undefined/null
                errors.extend(self.validate_view(view))
                
                # Validate actions
                errors.extend(self.validate_actions(view))
                
                # Validate stats
                errors.extend(self.validate_stats(view))
            
        except Exception as e:
            errors.append(f"Exception: {str(e)}")
        
        result = ViewTestResult(
            app_type=app_type,
            action=action,
            success=len(errors) == 0,
            errors=errors
        )
        self.results.append(result)
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run tests for all app views"""
        logger.info("=" * 60)
        logger.info("🧪 VIEW RENDERING TESTS")
        logger.info("=" * 60)
        
        if not self.view_generator:
            logger.error("❌ ViewGenerator not available")
            return {"success": False, "error": "Missing dependencies"}
        
        # Define all app types and actions to test
        test_cases = [
            # Documents
            ("documents", "show_all"),
            ("documents", "scan_new"),
            
            # Cameras
            ("cameras", "show_grid"),
            ("cameras", "show_motion"),
            
            # Sales
            ("sales", "dashboard"),
            ("sales", "show_dashboard"),
            
            # Home
            ("home", "temperature"),
            ("home", "lighting"),
            
            # Analytics
            ("analytics", "overview"),
            ("analytics", "chart"),
            
            # Internet
            ("internet", "weather"),
            ("internet", "crypto"),
            ("internet", "exchange"),
            ("internet", "rss"),
            
            # System
            ("system", "help"),
            ("system", "status"),
            ("system", "welcome"),
            
            # Files
            ("files", "list"),
            ("files", "documents"),
            ("files", "downloads"),
            
            # Cloud Storage
            ("cloud_storage", "dashboard"),
            ("cloud_storage", "connect_onedrive"),
            ("cloud_storage", "connect_nextcloud"),
            ("cloud_storage", "connect_gdrive"),
            
            # CurlLM
            ("curllm", "status"),
            ("curllm", "query"),
            
            # Registry
            ("registry", "show_all"),
            
            # Services
            ("services", "show_all"),
            
            # Monitoring
            ("monitoring", "show_all"),
        ]
        
        passed = 0
        failed = 0
        
        for app_type, action in test_cases:
            result = self.test_view(app_type, action)
            
            if result.success:
                passed += 1
                logger.info(f"  ✅ {app_type}/{action}")
            else:
                failed += 1
                logger.info(f"  ❌ {app_type}/{action}")
                for error in result.errors[:3]:  # Show first 3 errors
                    logger.info(f"      → {error}")
        
        logger.info("=" * 60)
        logger.info(f"📊 VIEW RENDERING TEST SUMMARY")
        logger.info(f"  Total:  {len(test_cases)}")
        logger.info(f"  Passed: {passed} ✅")
        logger.info(f"  Failed: {failed} ❌")
        logger.info("=" * 60)
        
        return {
            "success": failed == 0,
            "total": len(test_cases),
            "passed": passed,
            "failed": failed,
            "results": [
                {"app_type": r.app_type, "action": r.action, "success": r.success, "errors": r.errors}
                for r in self.results
            ]
        }


class CommandValidationTester:
    """Tests that commands are properly recognized and return valid views"""
    
    def __init__(self):
        try:
            from backend.main import VoiceCommandProcessor, ViewGenerator
            self.processor = VoiceCommandProcessor
            self.view_generator = ViewGenerator
        except ImportError as e:
            logger.error(f"Failed to import: {e}")
            self.processor = None
            self.view_generator = None
    
    def test_command(self, command: str) -> Dict[str, Any]:
        """Test a command and validate the response"""
        errors = []
        
        try:
            # Process command
            result = self.processor.process(command)
            
            if not result.get('recognized'):
                return {
                    "command": command,
                    "success": False,
                    "errors": ["Command not recognized"]
                }
            
            # Check result structure
            if not result.get('app_type'):
                errors.append("Missing app_type in result")
            if not result.get('action'):
                errors.append("Missing action in result")
            
            # Generate view
            view = self.view_generator.generate(
                result.get('app_type', 'system'),
                result.get('action', 'unknown')
            )
            
            if not view:
                errors.append("View generation returned None")
            elif not view.get('title'):
                errors.append("View missing title")
            
        except Exception as e:
            errors.append(f"Exception: {str(e)}")
        
        return {
            "command": command,
            "success": len(errors) == 0,
            "app_type": result.get('app_type') if 'result' in dir() else None,
            "action": result.get('action') if 'result' in dir() else None,
            "errors": errors
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run command validation tests"""
        logger.info("=" * 60)
        logger.info("🧪 COMMAND VALIDATION TESTS")
        logger.info("=" * 60)
        
        if not self.processor:
            logger.error("❌ VoiceCommandProcessor not available")
            return {"success": False, "error": "Missing dependencies"}
        
        # Commands to test
        commands = [
            "pokaż faktury",
            "pokaż kamery",
            "pokaż sprzedaż",
            "pogoda",
            "kursy walut",
            "rejestry",
            "pokaż pliki",
            "chmura",
            "połącz onedrive",
            "połącz nextcloud",
            "status llm",
            "pomoc",
            "start",
        ]
        
        passed = 0
        failed = 0
        results = []
        
        for cmd in commands:
            result = self.test_command(cmd)
            results.append(result)
            
            if result['success']:
                passed += 1
                logger.info(f"  ✅ '{cmd}' → {result.get('app_type')}/{result.get('action')}")
            else:
                failed += 1
                logger.info(f"  ❌ '{cmd}'")
                for error in result['errors'][:2]:
                    logger.info(f"      → {error}")
        
        logger.info("=" * 60)
        logger.info(f"📊 COMMAND VALIDATION SUMMARY")
        logger.info(f"  Total:  {len(commands)}")
        logger.info(f"  Passed: {passed} ✅")
        logger.info(f"  Failed: {failed} ❌")
        logger.info("=" * 60)
        
        return {
            "success": failed == 0,
            "total": len(commands),
            "passed": passed,
            "failed": failed,
            "results": results
        }


def main():
    # Run view rendering tests
    view_tester = ViewRenderingTester()
    view_results = view_tester.run_all_tests()
    
    print()
    
    # Run command validation tests
    cmd_tester = CommandValidationTester()
    cmd_results = cmd_tester.run_all_tests()
    
    # Overall summary
    print()
    print("=" * 60)
    print("📊 OVERALL TEST SUMMARY")
    print("=" * 60)
    
    all_passed = view_results.get('success', False) and cmd_results.get('success', False)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
