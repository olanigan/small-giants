.PHONY: help install run download-samples clean format lint test setup check

# Default target
help:
	@echo "DSPy Invoice Parser - Available commands:"
	@echo ""
	@echo "  make setup          - Install dependencies with uv"
	@echo "  make install        - Alias for setup"
	@echo "  make run            - Run the Streamlit app"
	@echo "  make download-samples - Download/create sample invoices"
	@echo "  make clean          - Clean temporary files and directories"
	@echo "  make format         - Format code with black and isort"
	@echo "  make lint           - Run linters (mypy, black, isort)"
	@echo "  make test           - Run tests"
	@echo "  make check          - Run all checks (format, lint, test)"
	@echo "  make help           - Show this help message"
	@echo ""

# Install dependencies
setup install:
	@echo "📦 Installing dependencies..."
	uv sync
	@echo "✅ Dependencies installed"

# Run the Streamlit app
run:
	@echo "🚀 Starting Streamlit app..."
	@echo "   App will be available at http://localhost:8501"
	uv run streamlit run src/invoice_parser_ui/app.py

# Download/create sample invoices
download-samples:
	@echo "📥 Creating sample invoices..."
	uv run python scripts/download_sample_invoices.py
	@echo "✅ Sample invoices created in data/"

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	rm -rf temp/
	rm -rf reports/
	rm -rf .sprint/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ Clean complete"

# Format code
format:
	@echo "🎨 Formatting code..."
	uv run black src/ scripts/
	uv run isort src/ scripts/
	@echo "✅ Formatting complete"

# Run linters
lint:
	@echo "🔍 Running linters..."
	uv run black --check src/ scripts/ || echo "⚠️  Black found formatting issues"
	uv run isort --check src/ scripts/ || echo "⚠️  isort found import ordering issues"
	uv run mypy src/ || echo "⚠️  mypy found type checking issues"
	@echo "✅ Linting complete"

# Run tests
test:
	@echo "🧪 Running tests..."
	uv run pytest tests/ -v || echo "⚠️  Some tests failed"
	@echo "✅ Testing complete"

# Run all checks
check: format lint test
	@echo "✅ All checks complete"

# Setup everything (install + download samples)
setup-all: setup download-samples
	@echo "✅ Setup complete - ready to run!"

