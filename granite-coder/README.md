# Granite Coder

![OneCode Platform](https://img.shields.io/badge/OneCode-Platform-blue)

A token-efficient coding agent designed for local LLMs like **IBM Granite 4**, leveraging the "Greedy" architecture.

## Overview

Granite Coder uses **OneCoder's kit and tldr** tools to intelligently explore codebases without overwhelming small context windows.

## Usage

This agent is designed to be run as an MCP server via the OneCoder CLI.

1.  **Index the Agent**:
    ```bash
    onecoder mcp index coding-agents/
    ```

2.  **Verify**:
    ```bash
    onecoder mcp list
    ```

## Development

```bash
# Install dependencies
uv sync

# Run standalone
uv run python -m src.server
```
