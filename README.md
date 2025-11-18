# Small Giants

Exploring GenAI and Analytics use-cases with Small Language Models and Reward Models.

## Overview

Small Giants is a curated collection of practical demonstrations showing how small language models (SLMs) and Retrieval models can power real-world AI applications. We focus on models in the 350M-3B parameter range, emphasizing efficiency, local inference, and structured outputs over raw scale.

### Why Small Giants?

- **Small doesn't mean simple**: Modern foundational models (LFMs) achieve remarkable performance in specialized domains
- **Local-first approach**: Run inference on your hardware with Ollama
- **Cost-effective**: Reduce API costs and improve privacy
- **Practical**: Built on proven architectures (DSPy, structured extraction, agent orchestration)
- **Research-friendly**: Playground for exploring scaling laws, reward models, and few-shot learning

## Current Use-Cases

### 📄 [Invoice Parser](./dspy-liquid-agent)

**Multimodal document processing with structured extraction**

Extract utility billing information (amount, currency, type) from invoice images using a two-stage pipeline:
- **Stage 1**: Vision-language model (Liquid AI LFM2-VL-3B) extracts text from images
- **Stage 2**: Compact extraction model (LFM2-1.2B-Extract) parses structured data

**Features:**
- Web UI with Streamlit
- Batch processing
- Multiple model providers (Ollama, Gemini, OpenAI)
- CSV/JSON export

**Stack:** DSPy, Liquid AI, Ollama, Streamlit, Pydantic

[→ See detailed documentation](./dspy-liquid-agent/README.md)

## Roadmap

Planned use-cases exploring advanced GenAI + Analytics concepts:

- **Financial Analytics Pipeline**: Multi-document reasoning across invoices/receipts/statements with time-series forecasting
- **Reward Model Framework**: Develop evaluators for extraction accuracy, confidence estimation, and model comparison
- **Entity Linking System**: Connect extracted data to knowledge bases for enriched analysis
- **Active Learning Loop**: Identify high-uncertainty predictions for human review and model improvement
- **Benchmark Suite**: Comparative evaluation of small models vs. larger alternatives on document understanding tasks

## Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) (for local inference)
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/olanigan/small-giants.git
cd small-giants

# Install dependencies (using uv for speed)
pip install uv
uv pip install -e ./dspy-liquid-agent
```

### Run Invoice Parser Demo

```bash
cd dspy-liquid-agent
make download-samples  # Optional: create sample invoices
make run              # Launch Streamlit app at http://localhost:8501
```

For detailed setup instructions, see [dspy-liquid-agent/README.md](./dspy-liquid-agent/README.md)

## Architecture

**Agent-based orchestration** using DSPy's modular framework:
- Separates concerns: model inference, data validation, UI
- Supports swappable model providers
- Structured output enforcement via Pydantic schemas
- Extensible for chain-of-thought and optimization

```
User Input → Agent → Stage 1 (Vision) → Stage 2 (Extraction) → Structured Output
```

## Tech Stack

| Component | Tools |
|-----------|-------|
| **Framework** | [DSPy](https://github.com/stanfordnlp/dspy) |
| **Models** | [Liquid AI LFMs](https://www.liquid.ai) |
| **Inference** | [Ollama](https://ollama.ai), OpenAI, Google Gemini |
| **UI** | [Streamlit](https://streamlit.io) |
| **Validation** | [Pydantic](https://docs.pydantic.dev) |
| **Dev Tools** | Black, isort, mypy, pytest |

## Contributing

We welcome contributions! Whether you're adding new use-cases, improving reward models, or enhancing existing pipelines:

1. Fork the repository
2. Create a feature branch
3. Follow existing code style (see Makefile linting commands)
4. Submit a pull request

See each use-case's directory for specific contribution guidelines.

## License

[MIT](LICENSE)

## Citations

If you use Small Giants in your research, please cite:

```bibtex
@software{small_giants_2024,
  author = {Olanigan, Ibrahim},
  title = {Small Giants: GenAI and Analytics with Small Language Models},
  url = {https://github.com/olanigan/small-giants},
  year = {2025}
}
```

## Resources

- [DSPy Documentation](https://github.com/stanfordnlp/dspy)
- [Liquid AI Models](https://www.liquid.ai/research)
- [Ollama Getting Started](https://ollama.ai/library)
- [LLM Efficiency Benchmarks](https://huggingface.co/spaces/open-llm-leaderboard/)

---

**Questions or ideas?** Open an issue or start a discussion in the repository.
