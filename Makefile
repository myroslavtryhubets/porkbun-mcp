.PHONY: help build up down restart logs clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the Docker image
	docker-compose build

up: ## Start the MCP server
	docker-compose up -d
	@echo "Porkbun MCP server is starting..."
	@echo "Health check: http://localhost:8000/health"
	@echo "API docs: http://localhost:8000/docs"
	@echo "MCP endpoint: http://localhost:8000/porkbun/mcp"

down: ## Stop the MCP server
	docker-compose down

restart: ## Restart the MCP server
	docker-compose restart

logs: ## View server logs
	docker-compose logs -f porkbun-mcp

clean: ## Remove containers, images, and volumes
	docker-compose down -v
	docker-compose rm -f
	docker rmi porkbun-mcp-porkbun-mcp 2>/dev/null || true

test: ## Test the server endpoints
	@echo "Testing health endpoint..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "Server not running"
	@echo "\nTesting root endpoint..."
	@curl -s http://localhost:8000/ | python -m json.tool || echo "Server not running"

install: ## Create .env file from example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created. Please edit it with your Porkbun API credentials."; \
	else \
		echo ".env file already exists."; \
	fi

