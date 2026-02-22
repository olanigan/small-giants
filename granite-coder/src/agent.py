import ollama
from rlm import RLM


class GreedyAgent:
    """
    Implements the Greedy Architecture for token-efficient coding.
    Supports two modes:
    - direct: Simple direct Ollama calls
    - rlm: Recursive Language Model for complex context-aware tasks
    """

    def __init__(
        self,
        model_name: str = "ibm/granite4",
        max_iterations: int = 3,
        mode: str = "direct",
    ):
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.mode = mode

    def run(self, task: str, path: str):
        if self.mode == "rlm":
            return self._run_rlm(task, path)
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
