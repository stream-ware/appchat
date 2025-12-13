# FILES - Main Makefile
.PHONY: help run user admin

help:
	@echo "📁 File Manager App"
	@echo "Usage: make -f Makefile.user <target>"

run: user

user:
	@$(MAKE) -f Makefile.user $(filter-out $@,$(MAKECMDGOALS))

%:
	@:
