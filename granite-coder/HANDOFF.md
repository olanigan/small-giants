# HANDOFF: File Read/Write Implementation

**Agent**: Next implementer
**Status**: ✅ Completed
**Created**: 2026-02-22
**Completed**: 2026-02-22

---

## Objective

Implement file read/write capability in Granite Coder using Ollama's Responses API (`/v1/responses`) with tools (function calling).

## Current State

- ✅ **Direct mode**: Simple Ollama chat (no file access)
- ✅ **RLM mode**: Recursive Language Model (no file access - treats prompt as context)
- ✅ **Responses mode**: Implemented with file tools

## Implementation Summary

### Files Modified
- `src/agent.py` - Added responses mode with TOOLS definition and execution methods
- `src/cli.py` - Added "responses" to mode choices
- `tests/test_agent.py` - Added comprehensive tests for responses mode

### Tools Implemented
| Tool | Status | Method |
|------|--------|--------|
| `read_file` | ✅ | `_tool_read_file()` |
| `write_file` | ✅ | `_tool_write_file()` |
| `list_dir` | ✅ | `_tool_list_dir()` |
| `search_files` | ✅ | `_tool_search_files()` |

### Security
- Path sandboxing via `_sanitize_path()` prevents directory traversal attacks

## Target State

Add a new mode: **`responses`**

This mode will:
1. Accept user task
2. Define file operation tools (read_file, write_file, list_dir)
3. Send to Ollama `/v1/responses` with tools
4. Parse function_call responses
5. Execute tools locally
6. Return final response

---

## Requirements

### 1. Core Implementation

Add to `src/agent.py`:

```python
class GreedyAgent:
    def __init__(self, ..., mode: str = "direct"):
        # Add responses mode support
        
    def _run_responses(self, task: str, path: str):
        # Implement tool-enabled responses API call
        # Handle function_call parsing and execution
```

### 2. Tools to Implement

| Tool | Description | Parameters |
|------|-------------|------------|
| `read_file` | Read file contents | `path: str` |
| `write_file` | Write content to file | `path: str`, `content: str` |
| `list_dir` | List directory contents | `path: str` |
| `search_files` | Search for pattern in files | `pattern: str`, `path: str` |

### 3. CLI Updates

Update `src/cli.py` to support new mode:

```bash
granite-coder solve "Read src/agent.py" --mode responses
granite-coder chat --mode responses
```

### 4. Testing

Create test files in `tests/`:

#### Test 1: Read File
```python
# Create test file
with open("test_input.txt", "w") as f:
    f.write("Hello from test file")

# Run agent
result = agent.run("Read test_input.txt and tell me what it says", ".", mode="responses")

# Assert
assert "Hello from test file" in result
```

#### Test 2: Write File
```python
# Run agent
result = agent.run("Write 'test content' to test_output.txt", ".", mode="responses")

# Assert
with open("test_output.txt") as f:
    assert f.read() == "test content"
```

#### Test 3: Read + Write Chain
```python
# Create input file
with open("input.txt", "w") as f:
    f.write("original")

# Run agent
result = agent.run("Read input.txt, change 'original' to 'modified', write to output.txt", ".", mode="responses")

# Assert
with open("output.txt") as f:
    assert f.read() == "modified"
```

---

## Technical Context

### Responses API Tool Flow

1. **Request**: Send task + tool definitions to `/v1/responses`
2. **Response**: May contain `function_call` in output
3. **Parse**: Extract `name` and `arguments` from function_call
4. **Execute**: Run tool locally
5. **Continue**: For full implementation, would need to loop with tool results

### Key Code References

- `RESPONSES.md` - Full API documentation
- `src/agent.py` - Current agent implementation
- `src/cli.py` - CLI commands

### Sample Tool Definition

```python
TOOLS = [
    {
        "type": "function",
        "name": "read_file",
        "description": "Read the contents of a file from the filesystem",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to read"
                }
            },
            "required": ["path"]
        }
    },
    {
        "type": "function", 
        "name": "write_file",
        "description": "Write content to a file on the filesystem",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    }
]
```

### Parse Function Call from Response

```python
import json

data = response.json()

for item in data.get('output', []):
    if item.get('type') == 'function_call':
        func_name = item.get('name')
        args = json.loads(item.get('arguments', '{}'))
        
        if func_name == 'read_file':
            result = read_file(args['path'])
        elif func_name == 'write_file':
            result = write_file(args['path'], args['content'])
```

---

## Acceptance Criteria

- [x] Agent can read files via `responses` mode
- [x] Agent can write files via `responses` mode  
- [x] Agent can list directories via `responses` mode
- [x] CLI accepts `--mode responses` flag
- [x] Tests pass for read, write, and combined operations
- [x] Error handling for invalid paths, permissions, etc.

---

## Notes

- Responses API is non-stateful - each request is independent
- For multi-turn tool use, would need to re-prompt with tool results (future enhancement)
- Security: Path sandboxing restricts to base directory only

---

## Usage

```bash
# Read a file
granite-coder solve "Read src/agent.py and summarize it" --mode responses

# Write a file
granite-coder solve "Create a hello.py with a main function" --mode responses

# Interactive mode with file access
granite-coder chat --mode responses
```

---

## Future Enhancements

- Multi-turn tool execution loop
- Streaming responses with tool calls
- Additional tools (grep, git operations)

**Reference**: See `RESPONSES.md` for full API details.
