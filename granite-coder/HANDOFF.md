# HANDOFF: File Read/Write Implementation

**Agent**: Next implementer
**Status**: To be implemented
**Created**: 2026-02-22

---

## Objective

Implement file read/write capability in Granite Coder using Ollama's Responses API (`/v1/responses`) with tools (function calling).

## Current State

- ✅ **Direct mode**: Simple Ollama chat (no file access)
- ✅ **RLM mode**: Recursive Language Model (no file access - treats prompt as context)
- ❌ **Responses mode**: Not implemented yet

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

- [ ] Agent can read files via `responses` mode
- [ ] Agent can write files via `responses` mode  
- [ ] Agent can list directories via `responses` mode
- [ ] CLI accepts `--mode responses` flag
- [ ] Tests pass for read, write, and combined operations
- [ ] Error handling for invalid paths, permissions, etc.

---

## Notes

- Responses API is non-stateful - each request is independent
- For multi-turn tool use, would need to re-prompt with tool results
- Start with single-turn: task → tool call → result
- Consider security: restrict to project directory only

---

## Next Steps

1. Implement `_run_responses()` in `src/agent.py`
2. Add tool execution helper functions
3. Update CLI with `--mode responses` option
4. Create test files in `tests/`
5. Run tests and validate

**Reference**: See `RESPONSES.md` for full API details.
