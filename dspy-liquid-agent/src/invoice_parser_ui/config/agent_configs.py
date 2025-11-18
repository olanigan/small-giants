"""Agent configurations for DSPy Invoice Parser."""

# Liquid AI model configuration
LIQUID_MODEL_CONFIG = {
    "provider": "ollama",
    "model": "lfm2:7b",  # Display name for Liquid AI models
    "base_url": "http://localhost:11434",
    "temperature": 0.1,
    "max_tokens": 1000,
}

# Default configuration
DEFAULT_MODEL = "liquid_ai"

# Invoice processing specific settings
INVOICE_CONFIG = {
    "supported_formats": ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"],
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "batch_size": 5,  # Process 5 invoices at a time
    "timeout": 300,  # 5 minutes timeout per invoice
}

# Liquid AI model display configuration
LIQUID_MODELS = {
    "vision": ["LFM2-VL-3B", "LFM2-VL-1.6B"],
    "extraction": ["LFM2-1.2B-Extract", "LFM2-350M-Extract"],
}
