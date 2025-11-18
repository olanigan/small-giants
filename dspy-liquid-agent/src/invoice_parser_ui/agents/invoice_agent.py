"""Invoice processing agent using DSPy and Liquid Foundational Models."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import dspy
except ImportError:
    dspy = None

try:
    from ollama import chat
except ImportError:
    chat = None

from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvoiceText(BaseModel):
    """Raw text extracted from invoice image."""

    description: str


class InvoiceData(BaseModel):
    """Structured invoice data."""

    utility: str
    amount: float
    currency: str


class InvoiceProcessingResult(BaseModel):
    """Complete invoice processing result including extracted text and structured data."""

    extracted_text: str
    utility: str
    amount: float
    currency: str


class InvoiceAgent:
    """DSPy agent for processing invoice images using Liquid models."""

    def __init__(
        self,
        image_model: str = "hf.co/LiquidAI/LFM2-VL-3B-GGUF:F16",
        extractor_model: str = "hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:F16",
        model_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the invoice processing agent.

        Args:
            image_model: Ollama model name for image-to-text processing
            extractor_model: Ollama model name for text-to-structured-data extraction
            model_config: DSPy model configuration
        """
        self.image_model = image_model
        self.extractor_model = extractor_model
        self.model_config = model_config or {}

        # Ensure models are available
        self._ensure_models()

        # Setup DSPy if config provided
        # Note: DSPy configuration is handled by the app, not here
        # to avoid thread conflicts. This agent primarily uses Ollama directly.
        if model_config and dspy:
            # Check if DSPy is available, but don't configure it here
            # Configuration should be done at the app level to avoid thread issues
            try:
                # Just check if DSPy is configured, don't configure it
                self.dspy_available = dspy.settings.lm is not None
            except Exception as e:
                logger.warning(f"DSPy check failed: {e}")
                self.dspy_available = False
        else:
            self.dspy_available = False

    def _ensure_models(self):
        """Ensure required Ollama models are downloaded."""
        try:
            import ollama

            # Check and pull image model
            try:
                ollama.show(self.image_model.split("/")[-1])
            except:
                logger.info(f"Pulling image model: {self.image_model}")
                ollama.pull(self.image_model)

            # Check and pull extractor model
            try:
                ollama.show(self.extractor_model.split("/")[-1])
            except:
                logger.info(f"Pulling extractor model: {self.extractor_model}")
                ollama.pull(self.extractor_model)

        except ImportError:
            logger.warning(
                "Ollama not available, models will be downloaded on first use"
            )
        except Exception as e:
            logger.error(f"Error ensuring models: {e}")

    def process_single_invoice(self, image_path: str) -> Optional[InvoiceProcessingResult]:
        """Process a single invoice image.

        Args:
            image_path: Path to the invoice image file

        Returns:
            Complete processing result with extracted text and structured data, or None if processing failed
        """
        logger.info(f"Processing invoice: {image_path}")

        # Step 1: Extract text from image
        invoice_text = self._image_to_text(image_path)
        if not invoice_text:
            logger.warning(f"No text extracted from {image_path}")
            return None

        # Step 2: Extract structured data from text
        invoice_data = self._text_to_structured_data(invoice_text)
        if not invoice_data:
            logger.warning(f"No structured data extracted from text")
            return None

        # Return complete result with both extracted text and structured data
        result = InvoiceProcessingResult(
            extracted_text=invoice_text.description,
            utility=invoice_data.utility,
            amount=invoice_data.amount,
            currency=invoice_data.currency,
        )

        logger.info(
            f"Successfully processed {image_path}: {result.utility} - {result.amount} {result.currency}"
        )
        return result

    def process_batch_invoices(
        self, image_paths: List[str]
    ) -> List[Optional[InvoiceProcessingResult]]:
        """Process multiple invoice images.

        Args:
            image_paths: List of paths to invoice image files

        Returns:
            List of complete processing results (None for failed processing)
        """
        results = []
        for image_path in image_paths:
            result = self.process_single_invoice(image_path)
            results.append(result)
        return results

    def _image_to_text(self, image_path: str) -> Optional[InvoiceText]:
        """Extract text content from invoice image using vision model."""
        if not chat:
            logger.error("Ollama not available for image processing")
            return None

        try:
            import ollama

            with open(image_path, "rb") as f:
                image_data = f.read()

            response = ollama.chat(
                model=self.image_model,
                messages=[
                    {
                        "role": "user",
                        "content": "Extract all text and information from this invoice image. Provide a detailed description of what you see, including any amounts, dates, company names, and billing details.",
                        "images": [image_data],
                    }
                ],
                format=InvoiceText.model_json_schema(),
                options={"temperature": 0.0},
            )

            response_content = response["message"]["content"]
            return InvoiceText.model_validate_json(response_content)

        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {e}")
            return None

    def _text_to_structured_data(
        self, invoice_text: InvoiceText
    ) -> Optional[InvoiceData]:
        """Extract structured bill data from text content."""
        if not chat:
            logger.error("Ollama not available for text extraction")
            return None

        try:
            import ollama

            system_prompt = """Extract the following information from the invoice text. Provide the information in the exact JSON format specified:

- utility: The type of utility or service being billed (e.g., electricity, water, gas, internet, phone)
- amount: The total amount due or billed amount (numeric value only, no currency symbols)
- currency: The currency code (e.g., USD, EUR, GBP, AUD)

If any information is not available, use appropriate defaults or empty strings."""

            response = ollama.chat(
                model=self.extractor_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": invoice_text.description},
                ],
                format=InvoiceData.model_json_schema(),
                options={"temperature": 0.0},
            )

            invoice_data = InvoiceData.model_validate_json(
                response["message"]["content"]
            )
            return invoice_data

        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get agent status and configuration."""
        return {
            "image_model": self.image_model,
            "extractor_model": self.extractor_model,
            "dspy_available": self.dspy_available,
            "model_config": self.model_config,
        }


# DSPy Signature for invoice processing (if DSPy is available)
if dspy:

    class InvoiceProcessingSignature(dspy.Signature):
        """DSPy signature for invoice processing workflow."""

        invoice_image = dspy.InputField(desc="Path to invoice image file")
        extracted_text = dspy.OutputField(desc="Raw text extracted from invoice")
        utility_type = dspy.OutputField(desc="Type of utility or service")
        amount = dspy.OutputField(desc="Billed amount")
        currency = dspy.OutputField(desc="Currency code")

    class DSPyInvoiceProcessor(dspy.Module):
        """DSPy module for invoice processing."""

        def __init__(self):
            super().__init__()
            self.extract_text = dspy.Predict("invoice_image -> extracted_text")
            self.extract_data = dspy.Predict(
                "extracted_text -> utility_type, amount, currency"
            )

        def forward(self, invoice_image: str) -> Dict[str, Any]:
            # Extract text from image
            text_result = self.extract_text(invoice_image=invoice_image)

            # Extract structured data from text
            data_result = self.extract_data(extracted_text=text_result.extracted_text)

            return {
                "extracted_text": text_result.extracted_text,
                "utility": data_result.utility_type,
                "amount": data_result.amount,
                "currency": data_result.currency,
            }
else:
    # Placeholder classes when DSPy is not available
    class InvoiceProcessingSignature:
        """Placeholder for DSPy signature when DSPy is not available."""

        pass

    class DSPyInvoiceProcessor:
        """Placeholder for DSPy processor when DSPy is not available."""

        pass
