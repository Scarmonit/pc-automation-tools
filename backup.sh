#!/bin/bash
set -e  # Exit on any error

echo "Creating backup of LLMStack configuration..."

# Check if LLMSTACK_HOME is set
if [ -z "$LLMSTACK_HOME" ]; then
    export LLMSTACK_HOME="$HOME/llmstack"
    echo "LLMSTACK_HOME not set, using default: $LLMSTACK_HOME"
fi

# Create backup directory
BACKUP_DIR="$HOME/llmstack-backups"
mkdir -p "$BACKUP_DIR"

# Create backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/llmstack-backup-$(date +%Y%m%d_%H%M%S).tar.gz"

echo "Creating backup: $BACKUP_FILE"

# Backup configuration (only include existing directories)
BACKUP_PATHS=""
[ -d ~/.ollama ] && BACKUP_PATHS="$BACKUP_PATHS ~/.ollama"
[ -d ~/.flowise ] && BACKUP_PATHS="$BACKUP_PATHS ~/.flowise"
[ -d ~/.continue ] && BACKUP_PATHS="$BACKUP_PATHS ~/.continue"
[ -d "$LLMSTACK_HOME/data" ] && BACKUP_PATHS="$BACKUP_PATHS $LLMSTACK_HOME/data"

if [ -n "$BACKUP_PATHS" ]; then
    tar -czf "$BACKUP_FILE" $BACKUP_PATHS || {
        echo "ERROR: Failed to create backup"
        exit 1
    }
    echo "✓ Backup created successfully: $BACKUP_FILE"
    echo "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
else
    echo "WARNING: No configuration directories found to backup"
fi