# ============================================
# REGISTRY MANAGER - Main Makefile
# ============================================

.PHONY: help run user admin

APP_NAME := registry
APP_DIR := $(shell pwd)

help:
	@echo "📦 Registry Manager - Main Makefile"
	@echo "===================================="
	@echo ""
	@echo "📁 3-Level Structure:"
	@echo "  make run    - System commands"
	@echo "  make user   - User commands (view only)"
	@echo "  make admin  - Admin commands (full access)"

run:
	@make -f Makefile.run help

user:
	@make -f Makefile.user help

admin:
	@make -f Makefile.admin help

run-%:
	@make -f Makefile.run $*

user-%:
	@make -f Makefile.user $*

admin-%:
	@make -f Makefile.admin $*

info:
	@echo '{"app": "$(APP_NAME)", "type": "manager", "admin_only": true}'
