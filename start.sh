#!/bin/bash
# Streamware MVP - Start Script

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   🎤 STREAMWARE MVP - Voice Dashboard Platform                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Determine compose command
if docker compose version &> /dev/null 2>&1; then
    COMPOSE="docker compose"
else
    COMPOSE="docker-compose"
fi

# Parse arguments
MODE=${1:-prod}

case $MODE in
    prod)
        echo "🚀 Starting Streamware in production mode..."
        $COMPOSE up -d streamware
        ;;
    dev)
        echo "🔧 Starting Streamware in development mode (with hot reload)..."
        $COMPOSE --profile dev up -d streamware-dev
        PORT=8001
        ;;
    test)
        echo "🧪 Running tests..."
        $COMPOSE up -d streamware
        sleep 5
        $COMPOSE --profile test run --rm test-runner
        exit 0
        ;;
    logs)
        echo "📜 Showing logs..."
        $COMPOSE logs -f
        exit 0
        ;;
    stop)
        echo "🛑 Stopping all services..."
        $COMPOSE down
        exit 0
        ;;
    *)
        echo "Usage: $0 [prod|dev|test|logs|stop]"
        echo ""
        echo "  prod  - Start in production mode (default)"
        echo "  dev   - Start in development mode with hot reload"
        echo "  test  - Run automated tests"
        echo "  logs  - Show container logs"
        echo "  stop  - Stop all services"
        exit 1
        ;;
esac

# Wait for service to be healthy
echo ""
echo "⏳ Waiting for service to be ready..."

PORT=${PORT:-8000}
for i in {1..30}; do
    if curl -s "http://localhost:$PORT/api/health" > /dev/null 2>&1; then
        echo ""
        echo "✅ Streamware is running!"
        echo ""
        echo "╔═══════════════════════════════════════════════════════════════╗"
        echo "║                                                               ║"
        echo "║   🌐 Open in browser: http://localhost:$PORT                  ║"
        echo "║                                                               ║"
        echo "║   Available commands:                                         ║"
        echo "║   • 'Pokaż faktury'  - Document scanner view                  ║"
        echo "║   • 'Pokaż kamery'   - Camera monitoring grid                 ║"
        echo "║   • 'Pokaż sprzedaż' - Sales dashboard                        ║"
        echo "║   • 'Pomoc'          - Show all commands                      ║"
        echo "║                                                               ║"
        echo "║   Run tests: ./start.sh test                                  ║"
        echo "║   View logs: ./start.sh logs                                  ║"
        echo "║   Stop:      ./start.sh stop                                  ║"
        echo "║                                                               ║"
        echo "╚═══════════════════════════════════════════════════════════════╝"
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "❌ Service failed to start. Check logs with: ./start.sh logs"
exit 1
