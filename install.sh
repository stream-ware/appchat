#!/bin/bash
# Streamware MVP - Instalator
# Automatyczna instalacja i konfiguracja

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   🎤 STREAMWARE MVP - INSTALATOR                              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
fi

echo -e "${YELLOW}Detected OS: $OS${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check Python
echo -e "${BLUE}[1/5] Checking Python...${NC}"
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
elif command_exists python; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}✗ Python not found${NC}"
    echo "Please install Python 3.9+ from https://python.org"
    exit 1
fi

# Check pip
echo -e "${BLUE}[2/5] Checking pip...${NC}"
if command_exists pip3; then
    echo -e "${GREEN}✓ pip3 found${NC}"
    PIP="pip3"
elif command_exists pip; then
    echo -e "${GREEN}✓ pip found${NC}"
    PIP="pip"
else
    echo -e "${RED}✗ pip not found${NC}"
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
    PIP="pip3"
fi

# Check Docker (optional)
echo -e "${BLUE}[3/5] Checking Docker (optional)...${NC}"
if command_exists docker; then
    DOCKER_VERSION=$(docker --version 2>&1 | awk '{print $3}' | tr -d ',')
    echo -e "${GREEN}✓ Docker $DOCKER_VERSION found${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ Docker not found (optional - for containerized deployment)${NC}"
    DOCKER_AVAILABLE=false
fi

# Create virtual environment
echo -e "${BLUE}[4/5] Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate venv and install dependencies
echo -e "${BLUE}[5/5] Installing Python dependencies...${NC}"
if [[ "$OS" == "windows" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || cat > .env << EOF
# Streamware MVP Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
DEBUG=false

# LLM Configuration (optional)
LLM_PROVIDER=none
# OPENAI_API_KEY=sk-...
# OLLAMA_HOST=http://localhost:11434
EOF
    echo -e "${GREEN}✓ Created .env configuration file${NC}"
fi

# Create necessary directories
mkdir -p data/documents data/cameras logs
echo -e "${GREEN}✓ Created data directories${NC}"

# Make scripts executable
chmod +x start.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ INSTALACJA ZAKOŃCZONA POMYŚLNIE!                         ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Aby uruchomić aplikację:"
echo ""
echo -e "  ${BLUE}# Aktywuj środowisko wirtualne:${NC}"
if [[ "$OS" == "windows" ]]; then
    echo -e "  source venv/Scripts/activate"
else
    echo -e "  source venv/bin/activate"
fi
echo ""
echo -e "  ${BLUE}# Uruchom serwer:${NC}"
echo -e "  python -m uvicorn backend.main:app --reload"
echo ""
echo -e "  ${BLUE}# Lub użyj start.sh:${NC}"
echo -e "  ./start.sh prod"
echo ""
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo -e "  ${BLUE}# Lub z Dockerem:${NC}"
    echo -e "  docker-compose up -d"
    echo ""
fi
echo -e "  ${BLUE}# Otwórz w przeglądarce:${NC}"
echo -e "  http://localhost:8000"
echo ""
echo -e "  ${BLUE}# Uruchom testy:${NC}"
echo -e "  python scripts/test_demo.py"
echo ""
