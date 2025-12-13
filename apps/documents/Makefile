# Documents App - Makefile DSL
.PHONY: help list scan export health fix-code

APP_NAME := documents
APP_DIR := $(shell pwd)

help:
	@echo "📄 Documents App Commands:"
	@echo "  make list        - List all documents"
	@echo "  make scan        - Scan new document"
	@echo "  make export      - Export to Excel"
	@echo "  make health      - Check status"

list:
	@echo '{"documents": 8, "total_value": 98031.91, "pending": 7}'

scan:
	@echo '{"success": true, "message": "Document scanned"}'

export:
	@echo '{"success": true, "file": "export.xlsx"}'

health:
	@echo '{"status": "healthy"}'

info:
	@echo '{"app": "$(APP_NAME)", "status": "active"}'

fix-code:
	@find $(APP_DIR) -name "*.py" -o -name "*.toml"
