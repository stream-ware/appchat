# CurlLM App - Main Makefile
.PHONY: help install status models query chat

help:
	@echo "🤖 CurlLM - Universal LLM Client"
	@echo ""
	@echo "Usage: make -f Makefile.[user|admin] <target>"
	@echo "  status   - Check LLM status"
	@echo "  models   - List available models"
	@echo "  query    - Query LLM (PROMPT=...)"

install:
	pip install curllm httpx

status:
	@python3 scripts/curllm_client.py status

models:
	@python3 scripts/curllm_client.py models
