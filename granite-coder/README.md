# Granite Coder

![OneCode Platform](https://img.shields.io/badge/OneCode-Platform-blue)

A token-efficient coding agent designed for local LLMs like **IBM Granite 4**, leveraging the "Greedy" architecture.

## Overview

Granite Coder uses **OneCoder's kit and tldr** tools to intelligently explore codebases without overwhelming small context windows. It supports multiple operation modes for different use cases.

## Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) - Python package manager
- [Ollama](https://ollama.ai) - Local LLM runtime
- IBM Granite 4 model (`ollama pull ibm/granite4`)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd granite-coder

# Install dependencies
make deps

# Or manually with uv
uv sync --extra dev
```

### Verify Setup

```bash
# Check Ollama status and Granite availability
make status
```

Expected output:
```
Ollama: ONLINE (X models)
Granite: AVAILABLE (ibm/granite4)
```

## Usage Modes

Granite Coder supports **three modes** for different scenarios:

| Mode | Description | Use Case |
|------|-------------|----------|
| `direct` | Simple Ollama chat | Quick questions, no file access |
| `rlm` | Recursive Language Model | Complex reasoning tasks |
| `responses` | Tool-enabled API | File read/write operations |

### Mode 1: Direct (Default)

Simple, fast responses without file system access.

```bash
# Quick question
uv run granite-coder solve "Explain async/await in Python"

# Interactive chat
uv run granite-coder chat
```

### Mode 2: RLM (Recursive Language Model)

For complex, context-aware tasks with iterative refinement.

```bash
uv run granite-coder solve "Design a REST API for a todo app" --mode rlm
```

### Mode 3: Responses (File Operations)

Enables file system tools for reading, writing, listing, and searching files.

```bash
# Read a file
uv run granite-coder solve "Read src/agent.py and summarize it" --mode responses

# Write a file
uv run granite-coder solve "Create a hello.py with a main function" --mode responses

# List directory
uv run granite-coder solve "List files in the src directory" --mode responses

# Search files
uv run granite-coder solve "Find all Python files in src matching '*.py'" --mode responses

# Interactive with file access
uv run granite-coder chat --mode responses
```

#### Available Tools (Responses Mode)

| Tool | Description | Parameters |
|------|-------------|------------|
| `read_file` | Read file contents | `path: str` |
| `write_file` | Write content to file | `path: str`, `content: str` |
| `list_dir` | List directory contents | `path: str` |
| `search_files` | Search for files by pattern | `pattern: str`, `path: str` |

#### Security

File operations are **sandboxed** to the project directory. Attempts to access files outside the base path will be blocked.

## Makefile Commands

```bash
make help        # Show all available commands
make deps        # Sync dependencies
make install     # Install as CLI tool
make dev         # Show CLI help
make chat        # Start interactive chat
make test        # Run quick test
make pytest      # Run full test suite
make lint        # Run linter
make format      # Format code
make status      # Check Ollama status
make clean       # Clean cache files
```

## Development

### Running Tests

```bash
# Quick test
make test

# Full test suite
make pytest

# Or manually
uv run --isolated pytest tests/ -v
```

### Code Quality

```bash
make lint      # Check for issues
make format    # Auto-format code
```

### Project Structure

```
granite-coder/
├── src/
│   ├── agent.py      # Core agent implementation
│   ├── cli.py        # CLI commands
│   └── server.py     # MCP server
├── tests/
│   └── test_agent.py # Test suite
├── Makefile          # Development commands
├── pyproject.toml    # Project configuration
└── README.md         # This file
```

## MCP Integration

Granite Coder can run as an MCP server for integration with OneCoder:

```bash
# Start MCP server
make mcp

# Or manually
uv run granite-coder mcp
```

### Index with OneCoder

```bash
# Index the agent
onecoder mcp index coding-agents/

# Verify
onecoder mcp list
```

## Examples

### Code Review

```bash
uv run granite-coder solve "Review src/agent.py for potential improvements" --mode responses
```

### Generate Documentation

```bash
uv run granite-coder solve "Read src/cli.py and generate docstrings for all functions" --mode responses
```

### Refactoring

```bash
uv run granite-coder solve "Suggest refactoring for the _run_responses method in src/agent.py" --mode responses
```

## Troubleshooting

### Ollama Not Running

```bash
# Start Ollama
ollama serve

# Pull Granite model
ollama pull ibm/granite4
```

### Import Errors

```bash
# Re-sync dependencies
make deps
```

### Tests Failing

```bash
# Clean and reinstall
make clean
make deps
make pytest
```

## License

MIT
