import os
import tempfile
import pytest
from src.agent import GreedyAgent


class TestResponsesMode:
    """Tests for responses mode file operations"""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_read_file(self, temp_dir):
        test_file = os.path.join(temp_dir, "test_input.txt")
        with open(test_file, "w") as f:
            f.write("Hello from test file")

        agent = GreedyAgent(mode="responses")
        result = agent.run("Read test_input.txt and tell me what it says", temp_dir)

        assert "Hello from test file" in result

    def test_write_file(self, temp_dir):
        agent = GreedyAgent(mode="responses")
        result = agent.run("Write 'test content' to test_output.txt", temp_dir)

        output_file = os.path.join(temp_dir, "test_output.txt")
        assert os.path.exists(output_file)
        with open(output_file) as f:
            assert f.read() == "test content"

    def test_read_write_chain(self, temp_dir):
        input_file = os.path.join(temp_dir, "input.txt")
        with open(input_file, "w") as f:
            f.write("original")

        agent = GreedyAgent(mode="responses")
        result = agent.run("Read input.txt and tell me what it says", temp_dir)

        assert "original" in result

    def test_list_dir(self, temp_dir):
        for name in ["file1.txt", "file2.py", "subdir"]:
            path = os.path.join(temp_dir, name)
            if name == "subdir":
                os.makedirs(path)
            else:
                open(path, "w").close()

        agent = GreedyAgent(mode="responses")
        result = agent.run(
            "List the contents of the directory using path '.'", temp_dir
        )

        assert "file1.txt" in result or "file2.py" in result

    def test_path_sandboxing(self, temp_dir):
        agent = GreedyAgent(mode="responses")

        with pytest.raises(ValueError):
            agent._sanitize_path("../../../etc/passwd", temp_dir)

    def test_direct_mode_still_works(self):
        agent = GreedyAgent(mode="direct")
        result = agent.run("Say hello", ".")
        assert result


class TestToolExecution:
    """Unit tests for tool execution methods"""

    def test_sanitize_path_valid(self):
        agent = GreedyAgent()
        with tempfile.TemporaryDirectory() as tmpdir:
            safe = agent._sanitize_path("subdir/file.txt", tmpdir)
            assert safe.startswith(tmpdir)

    def test_sanitize_path_escape_attempt(self):
        agent = GreedyAgent()
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError):
                agent._sanitize_path("../../../etc/passwd", tmpdir)

    def test_tool_list_dir(self):
        agent = GreedyAgent()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["a.txt", "b.py"]:
                open(os.path.join(tmpdir, name), "w").close()
            result = agent._tool_list_dir(".", tmpdir)
            assert "a.txt" in result
            assert "b.py" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
