#!/usr/bin/env python3
"""
DSPy Invoice Parser Streamlit UI

A web interface for processing invoice images using DSPy agents and Liquid Foundational Models.
"""

import csv
import hashlib
import io
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import configurations
LIQUID_MODEL_CONFIG = {}
LIQUID_MODELS = {}
try:
    from config.agent_configs import LIQUID_MODEL_CONFIG, LIQUID_MODELS

    CONFIG_AVAILABLE = True
except ImportError:
    st.error("Failed to import configurations")
    CONFIG_AVAILABLE = False

# Import invoice processing agent
InvoiceAgent = None
try:
    from agents.invoice_agent import InvoiceAgent

    AGENTS_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import invoice agent: {e}")
    AGENTS_AVAILABLE = False

# Initialize DSPy configuration flag (don't configure at module level)
# DSPy will be configured on-demand in process_invoices to avoid thread conflicts
DSPY_CONFIGURED = False

# Constants
PROGRESS_INITIALIZATION = 0
PROGRESS_AGENT_INIT = 20
PROGRESS_PROCESSING_START = 40
PROGRESS_OUTPUT_GENERATION = 90
PROGRESS_COMPLETE = 100
PROGRESS_PROCESSING_RANGE = 50  # 40-90 range for processing

CONTENT_PREVIEW_LENGTH = 50
TIMESTAMP_FORMAT = "%H:%M:%S"
DATE_FORMAT = "%Y%m%d_%H%M%S"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

TEMP_DIR = "temp"
REPORTS_DIR = "reports"
SPRINT_DIR = ".sprint"
LOG_FILE = "invoice_parser.log"

MODEL_PREFIX = "hf.co/LiquidAI/"
MODEL_SUFFIX = "-GGUF:F16"

AGENT_TYPES = {
    "invoice_parser": {
        "name": "📄 Invoice Parser",
        "description": "Process invoice images using Liquid Foundational Models",
        "parameters": {
            "image_files": {
                "type": "file_uploader",
                "help": "Upload invoice images (PNG, JPG, JPEG)",
            },
            "extractor_model": {
                "type": "select",
                "options": ["LFM2-1.2B-Extract", "LFM2-350M-Extract"],
                "default": "LFM2-1.2B-Extract",
            },
            "image_model": {
                "type": "select",
                "options": ["LFM2-VL-3B", "LFM2-VL-1.6B"],
                "default": "LFM2-VL-3B",
            },
            "output_format": {
                "type": "select",
                "options": ["csv", "json"],
                "default": "csv",
            },
        },
    }
}


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="DSPy Invoice Parser",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("📄 DSPy Invoice Parser")
    st.markdown("*Process invoice images using Liquid Foundational Models*")

    # Check if agents are available
    if not AGENTS_AVAILABLE:
        st.error(
            "❌ Invoice processing agent not available. Please check the implementation."
        )
        return

    # Show environment status
    # Check if environment is configured (but don't configure DSPy here to avoid thread conflicts)
    has_api_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OLLAMA_BASE_URL"))
    if not has_api_key and "dspy_configured" not in st.session_state:
        st.warning("⚠️ **Environment Setup Required**")
        st.markdown(
            """
        To use the invoice parser, you need to set up your environment:

        **For Gemini (Google AI):**
        1. Create a `.env` file with:
           ```
           GEMINI_API_KEY=your_gemini_api_key_here
           ```
        2. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

        **For Ollama (Local AI):**
        1. Install Ollama from [ollama.ai](https://ollama.ai)
        2. Run `ollama serve` to start the local server
        3. Pull the required models:
           ```bash
           ollama pull hf.co/LiquidAI/LFM2-VL-3B-GGUF:F16
           ollama pull hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:F16
           ```
        """
        )

    # Sidebar for agent configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Display Liquid AI model information
        if CONFIG_AVAILABLE:
            st.info("**Using Liquid AI Foundational Models**")
        else:
            st.error("Liquid AI model configuration not available")

        # Display agent info
        agent_info = AGENT_TYPES["invoice_parser"]
        st.info(f"**{agent_info['name']}**\n\n{agent_info['description']}")

        # Sample invoices section
        st.subheader("📦 Sample Invoices")
        sample_invoices_dir = Path("data")
        sample_invoices = []

        if sample_invoices_dir.exists():
            sample_invoices = sorted(
                list(sample_invoices_dir.glob("*.png"))
                + list(sample_invoices_dir.glob("*.jpg"))
                + list(sample_invoices_dir.glob("*.jpeg"))
            )

        if sample_invoices:
            selected_samples = st.multiselect(
                "Select Sample Invoices:",
                options=[f.name for f in sample_invoices],
                help="Choose from pre-downloaded sample invoices for testing",
            )
        else:
            st.info(
                "💡 No sample invoices found. Run `python scripts/download_sample_invoices.py` to create sample invoices."
            )
            selected_samples = []

        # Parameter inputs
        st.subheader("📝 Parameters")
        parameters = {}

        for param_name, param_config in agent_info["parameters"].items():
            if param_config["type"] == "file_uploader":
                parameters[param_name] = st.file_uploader(
                    param_name.replace("_", " ").title(),
                    type=["png", "jpg", "jpeg", "gif", "bmp"],
                    accept_multiple_files=True,
                    help=param_config.get("help", ""),
                )
            elif param_config["type"] == "select":
                parameters[param_name] = st.selectbox(
                    param_name.replace("_", " ").title(),
                    options=param_config["options"],
                    index=param_config["options"].index(param_config["default"]),
                    help=param_config.get("help", ""),
                )

        # Add selected samples to parameters
        if selected_samples:
            # Create a simple wrapper class to mimic Streamlit's UploadedFile
            class SampleFile:
                def __init__(self, path, name):
                    self.path = path
                    self.name = name
                    self._data = None

                def getbuffer(self):
                    if self._data is None:
                        with open(self.path, "rb") as f:
                            self._data = f.read()
                    return self._data

            sample_files = []
            for sample_name in selected_samples:
                sample_path = sample_invoices_dir / sample_name
                if sample_path.exists():
                    sample_files.append(SampleFile(sample_path, sample_name))

            # Merge with uploaded files
            if parameters.get("image_files"):
                parameters["image_files"] = (
                    list(parameters["image_files"]) + sample_files
                )
            else:
                parameters["image_files"] = sample_files

        # Process button
        process_button = st.button(
            "🚀 Process Invoices", type="primary", use_container_width=True
        )

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("⚡ Processing")

        # Status display
        status_placeholder = st.empty()

        # Progress bar
        progress_placeholder = st.empty()

        # Real-time trace display
        st.subheader("📝 Processing Log")
        trace_placeholder = st.empty()

        # Extracted text display
        st.subheader("📄 Extracted Text")
        extracted_text_placeholder = st.empty()

        # Results display
        st.subheader("📋 Results")
        results_placeholder = st.empty()

    with col2:
        st.header("📊 Statistics")

        # Processing metrics
        metrics_placeholder = st.empty()

        # Export options
        st.subheader("📤 Export")
        export_placeholder = st.empty()

    # Handle processing
    if process_button:
        if not parameters.get("image_files"):
            st.error(
                "Please upload at least one invoice image or select sample invoices"
            )
            return

        process_invoices(
            parameters,
            status_placeholder,
            progress_placeholder,
            trace_placeholder,
            extracted_text_placeholder,
            results_placeholder,
            metrics_placeholder,
            export_placeholder,
        )


def process_invoices(
    parameters,
    status_ph,
    progress_ph,
    trace_ph,
    extracted_text_ph,
    results_ph,
    metrics_ph,
    export_ph,
):
    """Process uploaded invoice images."""
    log_to_sprint("INVOICE_PROCESSING_START")

    # Store processing info for retries
    st.session_state["last_processing"] = {
        "parameters": parameters,
    }

    # Initialize processing tracking
    st.session_state.processing_trace = []
    st.session_state.extracted_texts = {}  # Store extracted text by filename
    # Create unique session ID for this processing run to avoid key conflicts
    st.session_state.processing_session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    start_time = datetime.now()

    def add_trace_entry(step_type, content, metadata=None):
        """Add an entry to the processing trace."""
        entry = {
            "timestamp": datetime.now(),
            "type": step_type,
            "content": content,
            "metadata": metadata or {},
        }
        st.session_state.processing_trace.append(entry)

        # Update display
        update_trace_display()

    def update_trace_display():
        """Update trace display as a text log."""
        if not st.session_state.processing_trace:
            trace_ph.info("Processing log will appear here...")
            return

        # Build log text
        log_lines = []
        for entry in st.session_state.processing_trace:
            time_str = entry["timestamp"].strftime(TIMESTAMP_FORMAT)
            step_type = entry["type"].upper()
            content = entry["content"]
            
            # Color coding based on type
            icon_map = {
                "START": "🚀",
                "SETUP": "⚙️",
                "PROCESSING": "⚡",
                "SUCCESS": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "OUTPUT": "📤",
            }
            icon = icon_map.get(step_type, "📝")
            
            log_line = f"[{time_str}] {icon} {step_type}: {content}"
            if entry.get("metadata"):
                log_line += f" | {entry['metadata']}"
            log_lines.append(log_line)

        # Display as text log with monospace font
        log_text = "\n".join(log_lines)
        trace_ph.code(log_text, language="text")

    def update_extracted_text_display():
        """Update extracted text display using read-only components to avoid key conflicts."""
        if not st.session_state.extracted_texts:
            extracted_text_ph.info("Extracted text will appear here after processing...")
            return

        # Display extracted text using hash-based keys that are stable per filename
        # This ensures each widget has a unique key even if called multiple times
        with extracted_text_ph.container():
            for filename, text in st.session_state.extracted_texts.items():
                with st.expander(f"📄 {filename}", expanded=False):
                    # Create a stable hash-based key that's unique per filename and session
                    # This prevents duplicate key errors when the function is called multiple times
                    key_hash = hashlib.md5(
                        f"{st.session_state.processing_session_id}_{filename}".encode()
                    ).hexdigest()[:12]
                    st.text_area(
                        "Extracted Text:",
                        value=text,
                        height=200,
                        key=f"extracted_{key_hash}",
                        label_visibility="collapsed",
                        disabled=True,  # Read-only to prevent editing
                    )

    # Start processing
    status_ph.info("🚀 Starting invoice processing...")
    add_trace_entry(
        "start", f"Processing {len(parameters['image_files'])} invoice images"
    )

    # Initialize progress
    progress_bar = progress_ph.progress(0)

    try:
        # Configure DSPy if not already configured in this session
        # Use session state to track configuration to avoid thread conflicts
        if "dspy_configured" not in st.session_state:
            try:
                import dspy
                from common.dspy_setup import setup_dspy

                # Get model config for DSPy setup
                dspy_model_config = {}
                if CONFIG_AVAILABLE:
                    dspy_model_config = LIQUID_MODEL_CONFIG.copy()

                lm = setup_dspy(dspy_model_config if dspy_model_config else None)
                dspy.configure(lm=lm)
                st.session_state["dspy_configured"] = True
                add_trace_entry("setup", "DSPy configured for invoice processing")
            except RuntimeError as dspy_e:
                # DSPy may already be configured in another thread - this is OK
                if "can only be changed by the thread that initially configured it" in str(dspy_e):
                    st.session_state["dspy_configured"] = True
                    add_trace_entry("setup", "DSPy already configured in another thread (using existing configuration)")
                else:
                    add_trace_entry("error", f"DSPy configuration failed: {dspy_e}")
                    raise
            except Exception as dspy_e:
                add_trace_entry("error", f"DSPy configuration failed: {dspy_e}")
                raise
        else:
            add_trace_entry(
                "setup", "DSPy already configured (using existing configuration)"
            )

        # Get model config
        model_config = {}
        if CONFIG_AVAILABLE:
            model_config = LIQUID_MODEL_CONFIG.copy()
            model_config.pop("provider", None)

        # Initialize invoice agent
        status_ph.info("🔧 Initializing invoice processing agent...")
        agent = InvoiceAgent(
            image_model=f"{MODEL_PREFIX}{parameters['image_model']}{MODEL_SUFFIX}",
            extractor_model=f"{MODEL_PREFIX}{parameters['extractor_model']}{MODEL_SUFFIX}",
            model_config=model_config,
        )
        progress_bar.progress(PROGRESS_AGENT_INIT)
        add_trace_entry("setup", "Invoice processing agent initialized")

        # Process invoices
        status_ph.info("⚡ Processing invoices...")
        progress_bar.progress(PROGRESS_PROCESSING_START)

        results = []
        for i, uploaded_file in enumerate(parameters["image_files"]):
            add_trace_entry(
                "processing",
                f"Processing invoice {i + 1}/{len(parameters['image_files'])}: {uploaded_file.name}",
            )

            # Save uploaded file temporarily
            temp_path = save_uploaded_file(uploaded_file)

            try:
                # Process single invoice
                result = agent.process_single_invoice(temp_path)
                if result:
                    result_dict = result.model_dump()
                    result_dict["file_name"] = uploaded_file.name
                    result_dict["processed_at"] = datetime.now().isoformat()
                    
                    # Store extracted text for display (will be shown at the end)
                    st.session_state.extracted_texts[uploaded_file.name] = result.extracted_text
                    
                    # Add trace entry for text extraction
                    text_preview = result.extracted_text[:100] + "..." if len(result.extracted_text) > 100 else result.extracted_text
                    add_trace_entry(
                        "processing", 
                        f"Text extracted from {uploaded_file.name}",
                        metadata={"preview": text_preview}
                    )
                    
                    # Remove extracted_text from result dict for CSV/JSON output
                    output_dict = {k: v for k, v in result_dict.items() if k != "extracted_text"}
                    results.append(output_dict)
                    
                    add_trace_entry(
                        "success", f"Successfully processed {uploaded_file.name}"
                    )
                else:
                    add_trace_entry(
                        "warning", f"No data extracted from {uploaded_file.name}"
                    )

            except Exception as e:
                add_trace_entry(
                    "error", f"Failed to process {uploaded_file.name}: {str(e)}"
                )
                continue

            finally:
                # Clean up temp file
                try:
                    if temp_path and os.path.exists(temp_path):
                        os.remove(temp_path)
                except OSError:
                    pass  # File may already be deleted

            # Update progress
            progress = (
                PROGRESS_PROCESSING_START
                + (i + 1) / len(parameters["image_files"]) * PROGRESS_PROCESSING_RANGE
            )
            progress_bar.progress(int(progress))

        # Generate output
        if results:
            timestamp = datetime.now().strftime(DATE_FORMAT)
            if parameters["output_format"] == "csv":
                output_data = generate_csv_output(results)
                output_filename = f"invoices_{timestamp}.csv"
                output_mime = "text/csv"
            else:
                output_data = json.dumps(results, indent=2)
                output_filename = f"invoices_{timestamp}.json"
                output_mime = "application/json"

            progress_bar.progress(PROGRESS_OUTPUT_GENERATION)
            add_trace_entry(
                "output",
                f"Generated {parameters['output_format'].upper()} output with {len(results)} processed invoices",
            )

            # Display results
            status_ph.success("✅ Processing completed!")
            progress_bar.progress(PROGRESS_COMPLETE)

            # Update extracted text display once at the end (avoids duplicate key errors)
            update_extracted_text_display()

            # Show results table
            df = pd.DataFrame(results)
            results_ph.dataframe(df)

            # Export options
            with export_ph.container():
                st.download_button(
                    label=f"📥 Download {parameters['output_format'].upper()}",
                    data=output_data,
                    file_name=output_filename,
                    mime=output_mime,
                    key="download_results",
                )

                # Share summary
                generated_time = datetime.now().strftime(DATETIME_FORMAT)
                share_text = f"""📄 Invoice Processing Summary

Processed {len(results)} invoices successfully
Format: {parameters["output_format"].upper()}
Generated: {generated_time}

Results include: utility, amount, currency for each invoice
"""
                if st.button("📋 Copy Summary"):
                    st.code(share_text)
                    st.success("Summary copied!")

        else:
            status_ph.warning("⚠️ No invoices were successfully processed")
            progress_bar.progress(PROGRESS_INITIALIZATION)

        # Update metrics
        total_duration = (datetime.now() - start_time).total_seconds()
        metrics_text = f"""
**Total Duration:** {total_duration:.2f}s
**Invoices Processed:** {len(results)}/{len(parameters["image_files"])}
**Success Rate:** {len(results) / len(parameters["image_files"]) * 100:.1f}%
**Output Format:** {parameters["output_format"].upper()}
"""
        metrics_ph.code(metrics_text, language="markdown")

        # Generate report
        generate_processing_report(
            parameters, results, st.session_state.processing_trace, total_duration
        )

    except Exception as e:
        status_ph.error(f"❌ Processing failed: {str(e)}")
        progress_bar.progress(PROGRESS_INITIALIZATION)

        tb_str = traceback.format_exc()
        error_content = f"Processing failed: {str(e)}\n\nTraceback:\n{tb_str}"
        add_trace_entry("error", error_content)

        # Calculate duration for error case
        error_duration = (datetime.now() - start_time).total_seconds()
        generate_processing_report(
            parameters, [], st.session_state.processing_trace, error_duration
        )

        log_to_sprint(f"INVOICE_PROCESSING_FAILED: {str(e)}")


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to temporary location."""
    temp_dir = Path(TEMP_DIR)
    temp_dir.mkdir(exist_ok=True)

    # Handle both Streamlit UploadedFile and our SampleFile wrapper
    if hasattr(uploaded_file, "path"):
        # It's a SampleFile wrapper - copy from source
        import shutil

        temp_path = temp_dir / uploaded_file.name
        shutil.copy2(uploaded_file.path, temp_path)
    else:
        # It's a Streamlit UploadedFile
        temp_path = temp_dir / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    return str(temp_path)


def generate_csv_output(results: list) -> str:
    """Generate CSV output from results."""
    if not results:
        return "file_name,processed_at,utility,amount,currency\n"

    output = io.StringIO()
    fieldnames = ["file_name", "processed_at", "utility", "amount", "currency"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

    return output.getvalue()


def generate_processing_report(parameters, results, processing_trace, duration):
    """Generate a processing report."""

    timestamp = datetime.now().strftime(DATETIME_FORMAT)
    report_content = f"""# DSPy Invoice Processing Report

**Timestamp:** {timestamp}
**Duration:** {duration:.2f} seconds
**Files Processed:** {len(parameters.get("image_files", []))}
**Successful Extractions:** {len(results)}
**Trace Steps:** {len(processing_trace)}

## Parameters
- **Image Model:** {parameters.get("image_model", "N/A")}
- **Extractor Model:** {parameters.get("extractor_model", "N/A")}
- **Output Format:** {parameters.get("output_format", "N/A")}

## Processing Trace

| Time | Type | Description |
|------|------|-------------|
"""

    for entry in processing_trace:
        time_str = entry["timestamp"].strftime(TIMESTAMP_FORMAT)
        step_type = entry["type"].upper()
        content = entry["content"]
        preview = (
            content[:CONTENT_PREVIEW_LENGTH] + "..."
            if len(content) > CONTENT_PREVIEW_LENGTH
            else content
        )
        report_content += f"| {time_str} | {step_type} | {preview} |\n"

    if results:
        report_content += f"\n## Results\n\n"
        for result in results:
            report_content += f"- **{result['file_name']}**: {result.get('utility', 'N/A')} - {result.get('amount', 'N/A')} {result.get('currency', 'N/A')}\n"

    # Save to reports directory
    reports_dir = Path(REPORTS_DIR)
    reports_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime(DATE_FORMAT)
    report_path = reports_dir / f"invoice_processing_{timestamp}.md"
    with open(report_path, "w") as f:
        f.write(report_content)

    log_to_sprint(f"REPORT_GENERATED: {report_path}")


def log_to_sprint(message):
    """Log message to .sprint directory."""
    sprint_dir = Path(SPRINT_DIR)
    sprint_dir.mkdir(exist_ok=True)

    log_file = sprint_dir / LOG_FILE
    timestamp = datetime.now().strftime(LOG_TIMESTAMP_FORMAT)

    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


if __name__ == "__main__":
    main()
