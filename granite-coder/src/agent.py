import os
import json
import glob as glob_module
import requests
import ollama
from rlm import RLM


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
                    "description": "The path to the file to read",
                }
            },
            "required": ["path"],
        },
    },
    {
        "type": "function",
        "name": "write_file",
        "description": "Write content to a file on the filesystem",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to the file"},
                "content": {"type": "string", "description": "The content to write"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "type": "function",
        "name": "list_dir",
        "description": "List the contents of a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The directory path to list"}
            },
            "required": ["path"],
        },
    },
    {
        "type": "function",
        "name": "search_files",
        "description": "Search for files matching a pattern in a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to match files",
                },
                "path": {"type": "string", "description": "Directory to search in"},
            },
            "required": ["pattern", "path"],
        },
    },
]


class GreedyAgent:
    """
    Implements the Greedy Architecture for token-efficient coding.
    Supports three modes:
    - direct: Simple direct Ollama calls
    - rlm: Recursive Language Model for complex context-aware tasks
    - responses: Tool-enabled responses API for file operations
    """

    def __init__(
        self,
        model_name: str = "ibm/granite4",
        max_iterations: int = 3,
        mode: str = "direct",
        base_url: str = "http://localhost:11434",
    ):
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.mode = mode
        self.base_url = base_url

    def run(self, task: str, path: str):
        if self.mode == "rlm":
            return self._run_rlm(task, path)
        if self.mode == "responses":
            return self._run_responses(task, path)
        return self._run_direct(task, path)

    def _run_direct(self, task: str, path: str):
        """Direct Ollama call - simple and fast"""
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": task,
                }
            ],
        )
        return response["message"]["content"]

    def _run_rlm(self, task: str, path: str):
        """RLM mode - for complex context-aware tasks"""
        rlm = RLM(
            backend="openai",
            backend_kwargs={
                "model_name": self.model_name,
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",
            },
            max_iterations=self.max_iterations,
        )

        full_prompt = f"Question: {task}\n\nProvide a direct, concise answer."

        result = rlm.completion(full_prompt)
        return result.response

    def _run_responses(self, task: str, path: str):
        """Responses mode - tool-enabled API for file operations"""
        response = requests.post(
            f"{self.base_url}/v1/responses",
            json={
                "model": self.model_name,
                "input": task,
                "tools": TOOLS,
            },
        )

        data = response.json()
        return self._process_response(data, path, task)

    def _process_response(self, data: dict, base_path: str, original_task: str) -> str:
        """Process response and execute any tool calls"""
        results = []

        for item in data.get("output", []):
            if item.get("type") == "function_call":
                func_name = item.get("name")
                args = json.loads(item.get("arguments", "{}"))
                result = self._execute_tool(func_name, args, base_path)
                results.append(f"Tool {func_name}: {result}")
            elif item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        results.append(content.get("text", ""))

        return "\n".join(results)

    def _execute_tool(self, name: str, args: dict, base_path: str) -> str:
        """Execute a tool locally with path sandboxing"""
        try:
            if name == "read_file":
                return self._tool_read_file(args.get("path", ""), base_path)
            elif name == "write_file":
                return self._tool_write_file(
                    args.get("path", ""), args.get("content", ""), base_path
                )
            elif name == "list_dir":
                return self._tool_list_dir(args.get("path", ""), base_path)
            elif name == "search_files":
                return self._tool_search_files(
                    args.get("pattern", ""), args.get("path", ""), base_path
                )
            return f"Unknown tool: {name}"
        except Exception as e:
            return f"Error executing {name}: {str(e)}"

    def _sanitize_path(self, path: str, base_path: str) -> str:
        """Ensure path is within base_path (security)"""
        abs_base = os.path.abspath(base_path)
        abs_path = os.path.abspath(os.path.join(base_path, path))
        if not abs_path.startswith(abs_base):
            raise ValueError(f"Path '{path}' is outside allowed directory")
        return abs_path

    def _tool_read_file(self, path: str, base_path: str) -> str:
        """Read file contents"""
        safe_path = self._sanitize_path(path, base_path)
        with open(safe_path, "r") as f:
            return f.read()

    def _tool_write_file(self, path: str, content: str, base_path: str) -> str:
        """Write content to file"""
        safe_path = self._sanitize_path(path, base_path)
        os.makedirs(os.path.dirname(safe_path), exist_ok=True) if os.path.dirname(
            safe_path
        ) else None
        with open(safe_path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {path}"

    def _tool_list_dir(self, path: str, base_path: str) -> str:
        """List directory contents"""
        safe_path = self._sanitize_path(path, base_path)
        entries = os.listdir(safe_path)
        return "\n".join(entries)

    def _tool_search_files(self, pattern: str, path: str, base_path: str) -> str:
        """Search for files matching pattern"""
        safe_path = self._sanitize_path(path, base_path)
        matches = glob_module.glob(os.path.join(safe_path, pattern), recursive=True)
        return "\n".join(os.path.relpath(m, safe_path) for m in matches)
