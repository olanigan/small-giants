# Granite Coder - Improvements

Areas identified for future iterations and enhancements.

## Current Issues

### 1. RLM Mode Not Working as Expected
- **Problem**: RLM mode returns irrelevant responses for simple Q&A tasks
- **Cause**: RLM architecture is designed for document analysis, not direct Q&A
- **Solution**: 
  - Use direct mode for simple tasks
  - Improve RLM prompt engineering
  - Consider using RLM only for code analysis tasks with actual file context

### 2. No Error Handling
- **Problem**: Agent fails silently on API errors, invalid models, etc.
- **Solution**: Add try/except blocks with user-friendly error messages

### 3. Chat Mode Has No History
- **Problem**: Each message is independent - no conversation context
- **Solution**: Implement message history in GreedyAgent

### 4. Limited Model Support
- **Problem**: Hardcoded to IBM Granite 4
- **Solution**: Add model configuration, support more Ollama models

### 5. No Code Execution
- **Problem**: Can generate code but not execute or test it
- **Solution**: Add sandboxed code execution capability

## Feature Ideas

### Short-term
- [ ] Add error handling with proper error messages
- [ ] Implement chat history
- [ ] Add model selection (qwen3, llama3, etc.)
- [ ] Support streaming responses
- [ ] Add verbose/debug mode

### Medium-term
- [ ] File system tools (read, write, search code)
- [ ] Code execution with sandboxing
- [ ] MCP server integration improvements
- [ ] Add tests

### Long-term
- [ ] Implement "kit and tldr" tools for codebase exploration
- [ ] Add multi-file analysis with RLM
- [ ] Implement agentic workflows
- [ ] Add evaluation framework

## Code Quality

### Documentation
- Add docstrings to all public methods
- Add type hints
- Create API documentation

### Testing
- Add unit tests for agent
- Add integration tests for CLI
- Add MCP server tests

### Performance
- Cache model responses
- Add request batching
- Optimize RLM iterations

## User Experience

### CLI Improvements
- Rich terminal output with colors
- Progress indicators
- Configuration file support (~/.granite-coder.yaml)
- Aliases for common commands

### Interactive Mode
- Syntax highlighting for code output
- Command history (up arrow)
- Auto-completion
- Clear command

---

*Last updated: 2026-02-22*
