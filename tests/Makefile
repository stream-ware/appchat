# Tests Makefile
# Run automated tests for apps and services

PYTHON ?= python3
VENV ?= $(abspath ../venv/bin/python)

.PHONY: help all apps services sandbox quick report clean

help:
	@echo "🧪 Streamware Test Runner"
	@echo ""
	@echo "Commands:"
	@echo "  all           - Run all tests (apps + services)"
	@echo "  apps          - Test all apps"
	@echo "  services      - Test all services"
	@echo "  sandbox       - Test sandbox functionality"
	@echo "  quick         - Quick tests (no sandbox)"
	@echo "  e2e           - Run E2E command tests"
	@echo "  views         - Run view rendering tests"
	@echo "  gui           - Run GUI/E2E tests (requires server on 8001)"
	@echo "  shell         - Run shell client tests"
	@echo "  integration   - Run integration tests"
	@echo "  ocr           - Run OCR integration tests"
	@echo "  ci            - Run CI tests"
	@echo "  ci-full       - Run full CI test suite"
	@echo "  report        - View last test report"
	@echo "  clean         - Remove test artifacts"
	@echo ""
	@echo "Shell Client Suites:"
	@echo "  shell-basic   - Basic command tests"
	@echo "  shell-internet- Internet integration tests"
	@echo "  shell-maps    - Maps/geocoding tests"
	@echo "  shell-cloud   - Cloud storage tests"
	@echo "  shell-files   - File management tests"
	@echo "  shell-diagnostic- Diagnostic tests"
	@echo ""
	@echo "Single tests:"
	@echo "  test-app APP=weather      - Test specific app"
	@echo "  test-service SVC=text2sql - Test specific service"

# ===== MAIN TARGETS =====

all:
	@cd .. && $(VENV) -m tests.test_runner

apps:
	@cd .. && $(VENV) -c "import asyncio; from tests.test_runner import TestRunner; r = TestRunner(); asyncio.run(r.test_all_apps())"

services:
	@cd .. && $(VENV) -c "import asyncio; from tests.test_runner import TestRunner; r = TestRunner(); asyncio.run(r.test_all_services())"

quick:
	@cd .. && $(VENV) -m tests.test_runner --no-sandbox

# ===== SINGLE TESTS =====

test-app:
	@cd .. && $(VENV) -m tests.test_runner --app $(APP)

test-service:
	@cd .. && $(VENV) -m tests.test_runner --service $(SVC)

# ===== SANDBOX TESTS =====

sandbox:
	@cd .. && $(VENV) -c "\
import asyncio; \
from services.sandbox import sandbox_manager; \
async def test(): \
    print('🔒 Testing Sandbox...'); \
    sid = sandbox_manager.create_sandbox('test'); \
    result = await sandbox_manager.run_in_sandbox(sid, 'echo Hello from sandbox'); \
    print(f'Result: {result}'); \
    sandbox_manager.destroy_sandbox(sid); \
    print('✅ Sandbox test passed'); \
asyncio.run(test())"

# ===== REPORT =====

report:
	@cat report.json 2>/dev/null | python3 -m json.tool || echo "No report found. Run 'make all' first."

report-summary:
	@cd .. && $(VENV) -c "\
import json; \
from pathlib import Path; \
r = json.load(open('tests/report.json')); \
print('📊 Test Report Summary'); \
print('-' * 40); \
for s in r.get('suites', []): \
    icon = '✅' if s['failed'] == 0 else '❌'; \
    print(f\"{icon} {s['name']}: {s['passed']}/{s['total']} passed\"); \
"

# ===== CLEANUP =====

clean:
	@rm -f report.json
	@rm -rf __pycache__ .pytest_cache
	@echo "✅ Test artifacts cleaned"

# ===== E2E COMMAND TESTS =====

e2e:
	@cd .. && source venv/bin/activate && python -m tests.test_e2e_commands

# ===== VIEW RENDERING TESTS =====

views:
	@cd .. && source venv/bin/activate && python -m tests.test_view_rendering

# ===== GUI TESTS =====

gui:
	@cd .. && $(VENV) -m tests.test_gui --url http://localhost:8001

gui-url:
	@cd .. && $(VENV) -m tests.test_gui --url $(URL)

# ===== SHELL CLIENT TESTS =====

shell:
	@cd .. && $(VENV) -m client.shell_client --suite all

shell-basic:
	@cd .. && $(VENV) -m client.shell_client --suite basic

shell-internet:
	@cd .. && $(VENV) -m client.shell_client --suite internet

shell-maps:
	@cd .. && $(VENV) -m client.shell_client --suite maps

shell-cloud:
	@cd .. && $(VENV) -m client.shell_client --suite cloud

shell-files:
	@cd .. && $(VENV) -m client.shell_client --suite files

shell-diagnostic:
	@cd .. && $(VENV) -m client.shell_client --suite diagnostic

# ===== INTEGRATION TESTS =====

integration:
	@cd .. && $(VENV) -m tests.test_shell_client

ocr:
	@cd .. && $(VENV) -m tests.test_ocr_integration

# ===== CI/CD =====

ci:
	@cd .. && $(VENV) -m tests.test_runner --no-sandbox -r tests/report.json
	@echo "CI tests completed"

ci-full:
	@cd .. && $(VENV) -m tests.test_runner -r tests/report.json
	@cd .. && $(VENV) -m tests.test_gui -r tests/gui_report.json
	@echo "Full CI tests completed"
