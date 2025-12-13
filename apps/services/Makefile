# ============================================
# SYSTEM SERVICES - Main Makefile
# ============================================

.PHONY: help run user admin

APP_NAME := services

help:
	@echo "🔧 System Services Manager"
	@echo "=========================="
	@echo ""
	@echo "  make run   - System commands"
	@echo "  make user  - User commands (view)"
	@echo "  make admin - Admin commands (control)"

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
	@echo '{"app": "services", "type": "system", "admin_only": true}'
