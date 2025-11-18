# DSPy Liquid Invoice Parser

A Streamlit-based web interface for processing invoice images using DSPy agents and Liquid Foundational Models.

## Features

- **Invoice Image Processing**: Upload and process multiple invoice images simultaneously
- **Liquid AI Models**: Uses LFM2-VL-3B for OCR and LFM2-1.2B-Extract for data extraction
- **DSPy Integration**: Leverages DSPy framework for agent-based processing workflows
- **Real-time Processing**: Live progress tracking and processing traces
- **Export Options**: Download results as CSV or JSON files
- **Error Recovery**: Intelligent error handling with retry mechanisms
- **Multiple Model Support**: Support for Ollama, Gemini, and OpenAI models

## Installation

### Prerequisites

1. **Python 3.9+**
2. **uv** package manager (recommended) or pip
3. **Ollama** (for local model inference) OR API keys for cloud models

### Setup with uv

```bash
# Clone or navigate to the project directory
cd dspy-liquid-agent

# Install dependencies
uv sync

# Activate the environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```


## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# For Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
```

### Ollama Setup (Recommended)

1. Install Ollama: https://ollama.ai/
2. Pull the required models:
```bash
ollama pull hf.co/LiquidAI/LFM2-VL-3B-GGUF:F16
ollama pull hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:F16
```

## Usage

### Running the Application

```bash
# With uv
uv run streamlit run src/invoice_parser_ui/app.py

# With pip
streamlit run src/invoice_parser_ui/app.py
```

### Using the Interface

1. **Upload Invoices**: Use the file uploader to select invoice images (PNG, JPG, JPEG, etc.)
2. **Configure Models**: Select the vision and extraction models
3. **Choose Output Format**: Select CSV or JSON output
4. **Process**: Click "🚀 Process Invoices" to start processing
5. **Download Results**: Use the export options to download processed data

## Architecture

### Core Components

- **InvoiceAgent**: Main processing agent using DSPy and Liquid models
- **Streamlit UI**: Web interface for file upload and result visualization
- **DSPy Integration**: Agent-based workflow orchestration
- **Model Management**: Support for multiple AI model providers

### Processing Pipeline

1. **Image Upload**: User uploads invoice images
2. **Text Extraction**: LFM2-VL-3B extracts text from images
3. **Data Structuring**: LFM2-1.2B-Extract converts text to structured data
4. **Validation**: Results are validated and formatted
5. **Export**: Final results are made available for download

## Development

### Project Structure

```
dspy-liquid-agent/
├── src/invoice_parser_ui/
│   ├── app.py                 # Main Streamlit application
│   ├── agents/
│   │   ├── invoice_agent.py   # Core invoice processing agent
│   │   └── __init__.py
│   ├── common/
│   │   ├── dspy_setup.py      # DSPy configuration utilities
│   │   └── __init__.py
│   ├── config/
│   │   ├── agent_configs.py   # Model and agent configurations
│   │   └── __init__.py
│   └── __init__.py
├── pyproject.toml             # Project configuration
├── README.md                  # This file
└── uv.lock                    # Dependency lock file
```

### Adding New Features

1. **New Agent Types**: Extend the `agents/` directory
2. **UI Components**: Add to `components/` directory
3. **Model Support**: Update `config/agent_configs.py` and `common/dspy_setup.py`

## Troubleshooting

### Common Issues

1. **"Model not found" errors**: Ensure Ollama models are downloaded
2. **Import errors**: Check that all dependencies are installed
3. **Connection errors**: Verify API keys and network connectivity
4. **Processing failures**: Check invoice image quality and format

### Logs

Check the `.sprint/invoice_parser.log` file for detailed error information.

## License

This project is part of the Liquid AI ecosystem. See individual component licenses for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For support and questions:
- Check the troubleshooting section above
- Review the Liquid AI documentation
- Join the Liquid AI Discord community
