# CLOUD STORAGE - Main Makefile
.PHONY: help run user admin

help:
	@echo "☁️ Cloud Storage App"
	@echo "Usage: make -f Makefile.[user|admin] <target>"

run: user

user:
	@$(MAKE) -f Makefile.user $(filter-out $@,$(MAKECMDGOALS))

admin:
	@$(MAKE) -f Makefile.admin $(filter-out $@,$(MAKECMDGOALS))

%:
	@:
