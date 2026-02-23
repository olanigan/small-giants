# Makefile for DSPy-Qdrant-Ollama RAG Benchmark

.PHONY: all setup clean run-baseline run-ragas-eval check-ollama check-qdrant pull-ollama-models

PROJECT_DIR := $(shell pwd)
DATA_DIR := $(PROJECT_DIR)/data
CSV_FILE := $(DATA_DIR)/rag_token_512.csv
VENV_DIR := $(PROJECT_DIR)/.venv

all: setup run-baseline run-ragas-eval

setup: install-deps check-ollama check-qdrant pull-ollama-models create-dummy-csv

install-deps:
	@echo "--- Installing Python dependencies with Poetry ---"
	@poetry install
	@echo "Python dependencies installed."

check-ollama:
	@echo "--- Checking Ollama installation and status ---"
	@ollama list > /dev/null 2>&1 || (echo "Ollama is not installed or not running."; exit 1)
	@echo "Ollama is installed and running."

pull-ollama-models:
	@echo "--- Pulling required Ollama models ---"
	@ollama pull nomic-embed-text || true
	@ollama pull gpt-oss:20b-cloud || true
	@ollama pull ibm/granite4 || true
	@echo "Ollama models pulling initiated."

check-qdrant:
	@echo "--- Checking Qdrant status ---"
	@curl -s http://localhost:6333/collections > /dev/null || (echo "Qdrant is not running on port 6333."; exit 1)
	@echo "Qdrant is running on port 6333."

create-dummy-csv:
	@echo "--- Creating dummy CSV file for testing ---"
	@mkdir -p $(DATA_DIR)
	@if [ ! -f $(CSV_FILE) ]; then \
		printf "text\nThis is the first document about AI.\nAI is transforming many industries.\nMachine learning is a subfield of AI.\nQdrant is a vector database.\nOllama runs large language models locally.\nDSPy optimizes prompts.\n" > $(CSV_FILE); \
		echo "Dummy CSV created at $(CSV_FILE)"; \
	else \
		echo "Dummy CSV already exists at $(CSV_FILE), skipping creation."; \
	fi

run-baseline:
	@echo "--- Running Baseline RAG Pipeline ---"
	@poetry run python main.py

run-ragas-eval:
	@echo "--- Running RAGAS Evaluation ---"
	@RUN_RAGAS_EVAL=true poetry run python main.py

clean:
	@echo "--- Cleaning up generated files and Qdrant collection ---"
	@rm -rf $(DATA_DIR)
	@poetry run python -c "from qdrant_client import QdrantClient; client = QdrantClient(host='localhost', port=6333); client.delete_collection(collection_name='rag_benchmark_collection') if client.collection_exists('rag_benchmark_collection') else None" || true
	@echo "Clean up complete."
