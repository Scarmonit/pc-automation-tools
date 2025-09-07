# LLMStack Development and Deployment Makefile

.PHONY: help install check deploy start stop restart logs clean benchmark validate

# Default target
help:
	@echo "LLMStack Development Commands:"
	@echo "  install    - Install dependencies and setup environment"
	@echo "  check      - Check system requirements"
	@echo "  deploy     - Deploy LLMStack in production mode"
	@echo "  dev        - Start development environment"
	@echo "  start      - Start all services"
	@echo "  stop       - Stop all services"
	@echo "  restart    - Restart all services"
	@echo "  logs       - Show service logs"
	@echo "  clean      - Clean up containers and volumes"
	@echo "  benchmark  - Run performance benchmarks"
	@echo "  validate   - Validate deployment"
	@echo "  monitor    - Setup monitoring stack"

# Install dependencies
install:
	@echo "Installing dependencies..."
	@./scripts/check_system.sh
	@./scripts/install_ollama.sh
	@echo "✓ Installation complete"

# Check system requirements
check:
	@./scripts/check_system.sh

# Deploy production stack
deploy:
	@echo "Deploying LLMStack..."
	@./scripts/deploy_llmstack.sh
	@./scripts/install_agents.sh
	@echo "✓ Deployment complete"

# Start development environment
dev:
	@echo "Starting development environment..."
	@docker compose -f docker-compose.development.yml up -d
	@echo "✓ Development environment started"
	@echo "  LLMStack: http://localhost:3000"
	@echo "  PgAdmin: http://localhost:5050"
	@echo "  Redis Commander: http://localhost:8081"

# Start services
start:
	@echo "Starting services..."
	@docker compose -f docker-compose.llmstack.yml up -d
	@echo "✓ Services started"

# Stop services
stop:
	@echo "Stopping services..."
	@docker compose -f docker-compose.llmstack.yml down
	@docker compose -f docker-compose.development.yml down
	@echo "✓ Services stopped"

# Restart services
restart: stop start

# Show logs
logs:
	@docker compose -f docker-compose.llmstack.yml logs -f

# Clean up
clean:
	@echo "Cleaning up containers and volumes..."
	@docker compose -f docker-compose.llmstack.yml down -v
	@docker compose -f docker-compose.development.yml down -v
	@docker system prune -f
	@echo "✓ Cleanup complete"

# Run benchmarks
benchmark:
	@./scripts/benchmark.sh

# Validate deployment
validate:
	@./scripts/validate_deployment.sh

# Setup monitoring
monitor:
	@./scripts/setup_monitoring.sh

# GPU setup for vLLM
gpu-setup:
	@echo "Setting up GPU acceleration..."
	@./scripts/setup_vllm.sh
	@docker compose -f vllm/docker-compose.yml up -d
	@echo "✓ GPU setup complete"

# Optimize performance
optimize:
	@./scripts/optimize.sh

# Full deployment pipeline
full-deploy: install deploy monitor validate
	@echo "✓ Full deployment complete"
	@echo "  LLMStack: http://localhost:3000"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana: http://localhost:3003"