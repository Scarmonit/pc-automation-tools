#!/bin/bash
# Stop all services
docker compose down
killall ollama
killall lm-studio.AppImage