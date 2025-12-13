# SYSTEM MONITOR - Main Makefile
.PHONY: help run user admin
help:
	@echo "📊 System Monitor"
	@echo "  make user - User commands"
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
