# Infrastructure Makefile
# Manage Docker/Podman services for Streamware

COMPOSE_FILE ?= docker/docker-compose.yml
RUNTIME ?= $(shell command -v podman-compose 2>/dev/null || command -v docker-compose 2>/dev/null || echo "docker compose")

.PHONY: help up down restart logs ps pull build clean status

help:
	@echo "🐳 Streamware Infrastructure Management"
	@echo ""
	@echo "Commands:"
	@echo "  up [SERVICE]     - Start services (all or specific)"
	@echo "  down             - Stop all services"
	@echo "  restart [SVC]    - Restart services"
	@echo "  logs [SVC]       - View service logs"
	@echo "  ps               - List running containers"
	@echo "  pull             - Pull latest images"
	@echo "  build            - Build images"
	@echo "  clean            - Remove all containers and volumes"
	@echo "  status           - Show service status"
	@echo ""
	@echo "Profiles:"
	@echo "  up-voice         - Start with TTS/STT services"
	@echo "  up-rag           - Start with vector database"
	@echo "  up-all           - Start all services"

# ===== CORE COMMANDS =====

up:
	$(RUNTIME) -f $(COMPOSE_FILE) up -d $(SERVICE)

down:
	$(RUNTIME) -f $(COMPOSE_FILE) down

restart:
	$(RUNTIME) -f $(COMPOSE_FILE) restart $(SERVICE)

logs:
	$(RUNTIME) -f $(COMPOSE_FILE) logs -f --tail=100 $(SERVICE)

ps:
	$(RUNTIME) -f $(COMPOSE_FILE) ps

pull:
	$(RUNTIME) -f $(COMPOSE_FILE) pull

build:
	$(RUNTIME) -f $(COMPOSE_FILE) build

clean:
	$(RUNTIME) -f $(COMPOSE_FILE) down -v --remove-orphans
	@echo "✅ All containers and volumes removed"

status:
	@echo "🔍 Service Status:"
	@$(RUNTIME) -f $(COMPOSE_FILE) ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# ===== PROFILE COMMANDS =====

up-voice:
	$(RUNTIME) -f $(COMPOSE_FILE) --profile voice up -d

up-rag:
	$(RUNTIME) -f $(COMPOSE_FILE) --profile rag up -d

up-all:
	$(RUNTIME) -f $(COMPOSE_FILE) --profile voice --profile rag up -d

# ===== SERVICE SHORTCUTS =====

ollama-up:
	$(RUNTIME) -f $(COMPOSE_FILE) up -d ollama

ollama-logs:
	$(RUNTIME) -f $(COMPOSE_FILE) logs -f ollama

redis-up:
	$(RUNTIME) -f $(COMPOSE_FILE) up -d redis

backend-up:
	$(RUNTIME) -f $(COMPOSE_FILE) up -d backend

backend-logs:
	$(RUNTIME) -f $(COMPOSE_FILE) logs -f backend

# ===== PODMAN SPECIFIC =====

podman-up:
	podman-compose -f podman/podman-compose.yml up -d

podman-down:
	podman-compose -f podman/podman-compose.yml down

# ===== DEVELOPMENT =====

dev-up:
	$(RUNTIME) -f $(COMPOSE_FILE) up -d redis ollama
	@echo "✅ Development services started (Redis, Ollama)"

dev-down:
	$(RUNTIME) -f $(COMPOSE_FILE) stop redis ollama
