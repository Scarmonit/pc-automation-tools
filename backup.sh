#!/bin/bash
# Backup configuration
tar -czf llmstack-backup-$(date +%Y%m%d).tar.gz \
  ~/.ollama \
  ~/.flowise \
  ~/.continue \
  "$LLMSTACK_HOME/data"