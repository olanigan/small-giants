# Ollama Responses API

Documentation for using Ollama's OpenAI-compatible Responses API (`/v1/responses`).

> **Note**: Added in Ollama v0.3.3

## Overview

Ollama supports the OpenAI Responses API at `/v1/responses`. This provides a more powerful alternative to the traditional Chat API, with native support for:

- ✅ Streaming (Server-Sent Events)
- ✅ Tools (function calling)
- ✅ Reasoning summaries (for thinking models like DeepSeek R1)
- ⚠️ Stateful requests (limited - see below)

## API Endpoint

```
POST http://localhost:11434/v1/responses
```

## Supported Features

### Request Fields

| Field | Supported | Notes |
|-------|-----------|-------|
| `model` | ✅ | Model name (e.g., `ibm/granite4`, `qwen3-coder-next:cloud`) |
| `input` | ✅ | Text input (replaces `messages` in Chat API) |
| `instructions` | ✅ | System instructions |
| `tools` | ✅ | Function definitions for tool calling |
| `stream` | ✅ | Streaming via SSE |
| `temperature` | ✅ | Sampling temperature |
| `top_p` | ✅ | Nucleus sampling |
| `max_output_tokens` | ✅ | Max tokens to generate |
| `truncation` | ✅ | Text truncation strategy |
| `previous_response_id` | ❌ | Stateful conversations not supported |
| `conversation` | ❌ | Stateful conversations not supported |

### Response Format

```json
{
  "id": "resp_505651",
  "object": "response",
  "created_at": 1771783212,
  "status": "completed",
  "model": "ibm/granite4",
  "output": [
    {
      "type": "message",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Hello there!"
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 36,
    "output_tokens": 4,
    "total_tokens": 40
  }
}
```

## Usage Examples

### Basic Request

```bash
curl -X POST http://localhost:11434/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ibm/granite4",
    "input": "Say hi in 3 words"
  }'
```

### Streaming Response

```bash
curl -X POST http://localhost:11434/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ibm/granite4",
    "input": "Say hi in 3 words",
    "stream": true
  }'
```

### With Tools (Function Calling)

```python
import requests

response = requests.post(
    'http://localhost:11434/v1/responses',
    json={
        'model': 'ibm/granite4',
        'input': 'Read the file src/agent.py',
        'tools': [
            {
                'type': 'function',
                'name': 'read_file',
                'description': 'Read contents of a file',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path': {'type': 'string'}
                    },
                    'required': ['path']
                }
            }
        ]
    }
)

data = response.json()

# Check for function calls in output
for item in data.get('output', []):
    if item.get('type') == 'function_call':
        func_name = item.get('name')
        args = json.loads(item.get('arguments', '{}'))
        print(f"Tool call: {func_name}({args})")
```

### Streaming with Tools

```python
import requests

response = requests.post(
    'http://localhost:11434/v1/responses',
    json={
        'model': 'ibm/granite4',
        'input': 'Read /tmp/test.txt',
        'tools': [...],
        'stream': True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        event = json.loads(line.decode('utf-8')[5:])
        event_type = event.get('type')
        
        if event_type == 'response.output_text.delta':
            print(event['delta'], end='', flush=True)
        elif event_type == 'response.output_item.added':
            # New output item (could be function_call)
            pass
```

## Architecture: Tool Execution Flow

Unlike OpenAI's Responses API which auto-executes tools, Ollama returns **function_call requests** that require manual handling:

```
┌─────────────────────────────────────────────────────────────┐
│                    Request with Tools                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Model Response                            │
│  - output: [{"type": "function_call", "name": "...",       │
│              "arguments": "{\"path\": \"/tmp/foo\"}"}]      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Manual Execution Required                    │
│  1. Parse function_call from response                       │
│  2. Execute tool locally                                   │
│  3. (Optional) Send result back for next response          │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Pattern

```python
import requests
import json

class OllamaResponses:
    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        
    def chat(self, prompt: str, tools: list = None, stream: bool = False):
        """Simple chat without tool execution"""
        response = requests.post(
            f"{self.base_url}/v1/responses",
            json={
                "model": self.model,
                "input": prompt,
                "tools": tools or [],
                "stream": stream
            }
        )
        return response.json()
    
    def chat_with_tools(self, prompt: str, tools: list, max_turns: int = 3):
        """Chat with tool execution loop"""
        messages = [{"role": "user", "content": prompt}]
        
        for turn in range(max_turns):
            # Send request
            response = requests.post(
                f"{self.base_url}/v1/responses",
                json={
                    "model": self.model,
                    "input": prompt if turn == 0 else "",  # Only first turn uses input
                    # For subsequent turns, would need different approach
                    # (Ollama doesn't support conversation state)
                }
            )
            
            data = response.json()
            
            # Check for function calls
            function_calls = []
            for item in data.get('output', []):
                if item.get('type') == 'function_call':
                    function_calls.append({
                        'name': item.get('name'),
                        'arguments': json.loads(item.get('arguments', '{}'))
                    })
            
            if not function_calls:
                # No more tools - return final response
                return self._extract_text(data)
            
            # Execute tools and continue (simplified - non-stateful)
            # Note: Need to re-prompt with tool results for non-stateful API
            for call in function_calls:
                result = self._execute_tool(call['name'], call['arguments'])
                prompt = f"Previous: {prompt}\nTool: {call['name']}\nResult: {result}\nContinue:"
        
        return "Max turns reached"
    
    def _execute_tool(self, name: str, args: dict):
        """Execute a tool locally"""
        # Implement your tools here
        if name == 'read_file':
            with open(args['path']) as f:
                return f.read()
        return f"Unknown tool: {name}"
    
    def _extract_text(self, response: dict) -> str:
        """Extract text from response"""
        parts = []
        for item in response.get('output', []):
            if item.get('type') == 'message':
                for content in item.get('content', []):
                    if content.get('type') == 'output_text':
                        parts.append(content.get('text', ''))
        return ''.join(parts)
```

## Comparison: Chat API vs Responses API

| Feature | Chat API (`/v1/chat`) | Responses API (`/v1/responses`) |
|---------|----------------------|--------------------------------|
| Simplicity | ✅ Simple | More complex |
| Streaming | ✅ | ✅ |
| Tools | ✅ (auto-execute) | ⚠️ (manual) |
| Stateful | ✅ (messages array) | ❌ (limited) |
| Reasoning | Basic | ✅ (summaries) |
| Input format | `messages` | `input` |

## Limitations

1. **No Stateful Conversations**: Cannot use `previous_response_id` or `conversation`
2. **Manual Tool Execution**: Tools must be executed client-side
3. **Limited Documentation**: Fewer examples compared to Chat API

## Use Cases

### When to use Chat API
- Simple chat applications
- Stateful conversations
- Auto tool execution

### When to use Responses API
- Need reasoning summaries
- Want OpenAI-compatible interface
- Custom tool execution logic
- Future-proofing (OpenAI standard)

## References

- [OpenAI Responses API Docs](https://platform.openai.com/docs/api-reference/responses)
- [Ollama GitHub - Responses API Issue](https://github.com/ollama/ollama/issues/11586)
- [Ollama Documentation](https://github.com/ollama/ollama)

---

*Last updated: 2026-02-22*
