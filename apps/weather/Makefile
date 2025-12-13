# ============================================
# WEATHER APP - Main Makefile (Entry Point)
# Includes: Makefile.run, Makefile.user, Makefile.admin
# ============================================

.PHONY: help run user admin info

APP_NAME := weather
APP_DIR := $(shell pwd)

help:
	@echo "🌤️ Weather App - Main Makefile"
	@echo "==============================="
	@echo ""
	@echo "📁 3-Level Makefile Structure:"
	@echo "  make run    - System/Service commands (DevOps)"
	@echo "  make user   - Daily use commands (End user)"
	@echo "  make admin  - Configuration commands (Admin)"
	@echo ""
	@echo "Quick commands:"
	@echo "  make run-start    - Start service"
	@echo "  make run-health   - Check health"
	@echo "  make user-pogoda  - Show weather"
	@echo "  make admin-config - Show config"
	@echo ""
	@echo "Or use directly:"
	@echo "  make -f Makefile.run help"
	@echo "  make -f Makefile.user help"
	@echo "  make -f Makefile.admin help"

# Show Makefile.run help
run:
	@make -f Makefile.run help

# Show Makefile.user help
user:
	@make -f Makefile.user help

# Show Makefile.admin help
admin:
	@make -f Makefile.admin help

# Shortcuts for run commands
run-%:
	@make -f Makefile.run $*

# Shortcuts for user commands
user-%:
	@make -f Makefile.user $*

# Shortcuts for admin commands
admin-%:
	@make -f Makefile.admin $*

# App info
info:
	@echo '{"app": "$(APP_NAME)", "dir": "$(APP_DIR)", "makefiles": ["Makefile.run", "Makefile.user", "Makefile.admin"]}'

# Validate all
validate:
	@echo "Validating $(APP_NAME)..."
	@python3 -c "import tomllib; tomllib.load(open('manifest.toml', 'rb')); print('✅ manifest.toml')"
	@test -f .env && echo "✅ .env" || echo "❌ .env missing"
	@test -f Makefile.run && echo "✅ Makefile.run" || echo "❌ Makefile.run missing"
	@test -f Makefile.user && echo "✅ Makefile.user" || echo "❌ Makefile.user missing"
	@test -f Makefile.admin && echo "✅ Makefile.admin" || echo "❌ Makefile.admin missing"
