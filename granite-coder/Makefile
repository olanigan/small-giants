# ============================================================================
# Granite Coder - Makefile
# ============================================================================

# Default target
.PHONY: help
help:
	@echo "Granite Coder - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev        Run in development mode (CLI)"
	@echo "  make chat       Start interactive chat"
	@echo "  make mcp        Run as MCP server"
	@echo "  make test       Run tests"
	@echo ""
	@echo "Installation:"
	@echo "  make install    Install as CLI tool via uv"
	@echo "  make reinstall  Reinstall (sync + install)"
	@echo "  make deps       Sync dependencies only"
	@echo ""
	@echo "Utilities:"
	@echo "  make status     Check Ollama status"
	@echo "  make clean      Clean cache files"
	@echo "  make lint       Run linter"
	@echo "  make format     Format code"

# ============================================================================
# Development
# ============================================================================

.PHONY: dev
dev:
	@echo "Running Granite Coder CLI..."
	uv run granite-coder --help

.PHONY: chat
chat:
	@echo "Starting interactive chat..."
	uv run granite-coder chat

.PHONY: mcp
mcp:
	@echo "Starting MCP server..."
	uv run granite-coder mcp

# Run a quick test
.PHONY: test
test:
	@echo "Running quick test..."
	uv run granite-coder solve "What is 2+2?"

.PHONY: pytest
pytest:
	@echo "Running pytest..."
	uv run pytest tests/ -v

# ============================================================================
# Installation
# ============================================================================

.PHONY: install
install:
	@echo "Installing granite-coder CLI via uv..."
	uv tool install -e .

.PHONY: reinstall
reinstall: deps install

.PHONY: deps
deps:
	@echo "Syncing dependencies..."
	uv sync

# ============================================================================
# Utilities
# ============================================================================

.PHONY: status
status:
	uv run granite-coder status

.PHONY: clean
clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete."

.PHONY: lint
lint:
	@echo "Running linter..."
	uv run ruff check src/

.PHONY: format
format:
	@echo "Formatting code..."
	uv run ruff format src/

# ============================================================================
# Shortcuts for common tasks
# ============================================================================

.PHONY: run
run: dev

.PHONY: solve
solve:
	@uv run granite-coder solve "$(TASK)"
