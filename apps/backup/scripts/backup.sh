#!/bin/bash
# Backup Manager Script

BACKUP_DIR="${BACKUP_DIR:-/tmp/streamware-backups}"
APPS_DIR="$(dirname "$(dirname "$(dirname "$0")")")"

case "$1" in
    create)
        mkdir -p "$BACKUP_DIR"
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
        tar -czf "$BACKUP_FILE" -C "$APPS_DIR" . 2>/dev/null
        echo "{\"success\": true, \"file\": \"$BACKUP_FILE\", \"timestamp\": \"$TIMESTAMP\"}"
        ;;
    list)
        FILES=$(ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{print "{\"file\": \""$NF"\", \"size\": \""$5"\"}"}' | paste -sd,)
        echo "{\"backups\": [$FILES]}"
        ;;
    restore)
        if [ -f "$2" ]; then
            tar -xzf "$2" -C "$APPS_DIR" 2>/dev/null
            echo "{\"success\": true, \"restored\": \"$2\"}"
        else
            echo "{\"success\": false, \"error\": \"File not found\"}"
        fi
        ;;
    *)
        echo "{\"commands\": [\"create\", \"list\", \"restore\"]}"
        ;;
esac
