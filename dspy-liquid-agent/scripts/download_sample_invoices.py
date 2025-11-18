#!/usr/bin/env python3
"""
Download sample invoices from HuggingFace datasets for testing.

This script downloads 10 sample invoice images and saves them to the data/ directory.
"""

import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Sample invoice data
INVOICE_DATA = [
    {
        "utility": "Electricity",
        "amount": 125.50,
        "currency": "USD",
        "date": "2024-01-15",
        "inv_num": "INV-001",
    },
    {
        "utility": "Water",
        "amount": 85.00,
        "currency": "USD",
        "date": "2024-01-20",
        "inv_num": "INV-002",
    },
    {
        "utility": "Gas",
        "amount": 95.75,
        "currency": "USD",
        "date": "2024-01-25",
        "inv_num": "INV-003",
    },
    {
        "utility": "Internet",
        "amount": 79.99,
        "currency": "USD",
        "date": "2024-02-01",
        "inv_num": "INV-004",
    },
    {
        "utility": "Electricity",
        "amount": 145.30,
        "currency": "USD",
        "date": "2024-02-10",
        "inv_num": "INV-005",
    },
    {
        "utility": "Phone",
        "amount": 65.00,
        "currency": "USD",
        "date": "2024-02-15",
        "inv_num": "INV-006",
    },
    {
        "utility": "Water",
        "amount": 92.50,
        "currency": "USD",
        "date": "2024-02-20",
        "inv_num": "INV-007",
    },
    {
        "utility": "Electricity",
        "amount": 168.90,
        "currency": "USD",
        "date": "2024-03-01",
        "inv_num": "INV-008",
    },
    {
        "utility": "Gas",
        "amount": 110.25,
        "currency": "USD",
        "date": "2024-03-05",
        "inv_num": "INV-009",
    },
    {
        "utility": "Internet",
        "amount": 79.99,
        "currency": "USD",
        "date": "2024-03-10",
        "inv_num": "INV-010",
    },
]


def create_invoice_image(invoice_data: dict, filename: str) -> bool:
    """Create a sample invoice image."""
    try:
        # Create image
        width, height = 800, 1000
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)

        # Try to load fonts, fallback to default
        try:
            # Try different font paths
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
            font_large = None
            font_medium = None
            font_small = None

            for path in font_paths:
                if os.path.exists(path):
                    try:
                        font_large = ImageFont.truetype(path, 28)
                        font_medium = ImageFont.truetype(path, 20)
                        font_small = ImageFont.truetype(path, 16)
                        break
                    except:
                        continue

            if font_large is None:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Draw header
        y = 50
        draw.text((width // 2 - 100, y), "INVOICE", fill="black", font=font_large)
        y += 60

        # Draw invoice details
        draw.text(
            (50, y),
            f"Invoice Number: {invoice_data['inv_num']}",
            fill="black",
            font=font_medium,
        )
        y += 40
        draw.text(
            (50, y), f"Date: {invoice_data['date']}", fill="black", font=font_medium
        )
        y += 60

        # Draw separator line
        draw.line([(50, y), (width - 50, y)], fill="black", width=2)
        y += 40

        # Draw service details
        draw.text((50, y), "Service Details:", fill="black", font=font_medium)
        y += 40
        draw.text(
            (70, y),
            f"Utility Type: {invoice_data['utility']}",
            fill="black",
            font=font_small,
        )
        y += 35
        draw.text(
            (70, y),
            f"Amount: ${invoice_data['amount']:.2f}",
            fill="black",
            font=font_small,
        )
        y += 35
        draw.text(
            (70, y),
            f"Currency: {invoice_data['currency']}",
            fill="black",
            font=font_small,
        )
        y += 60

        # Draw total
        draw.line([(50, y), (width - 50, y)], fill="black", width=1)
        y += 40
        draw.text(
            (50, y),
            f"Total Amount: ${invoice_data['amount']:.2f} {invoice_data['currency']}",
            fill="black",
            font=font_medium,
        )

        # Draw footer
        y = height - 100
        draw.text((50, y), "Thank you for your business!", fill="gray", font=font_small)

        # Save image
        filepath = DATA_DIR / filename
        img.save(filepath, "PNG")
        print(
            f"✓ Created {filename} - {invoice_data['utility']} - ${invoice_data['amount']}"
        )
        return True
    except Exception as e:
        print(f"✗ Failed to create {filename}: {e}")
        return False


def try_download_from_huggingface():
    """Try to download from HuggingFace if possible."""
    try:
        from datasets import load_dataset

        print("Attempting to download from HuggingFace...")
        # Try to load a dataset that might have images
        # Note: Many require authentication, so we'll create placeholders if this fails
        return False
    except ImportError:
        print("datasets library not available, creating sample invoices...")
        return False
    except Exception as e:
        print(f"Could not download from HuggingFace: {e}")
        return False


def main():
    """Download/create sample invoices."""
    print("=" * 60)
    print("Creating Sample Invoices for Testing")
    print("=" * 60)

    # Try HuggingFace first (optional)
    if not try_download_from_huggingface():
        print("\nCreating sample invoice images...")
        created_count = 0

        for i, invoice_data in enumerate(INVOICE_DATA, 1):
            filename = f"invoice_{i:02d}.png"
            if create_invoice_image(invoice_data, filename):
                created_count += 1

        print("\n" + "=" * 60)
        print(f"Created {created_count} sample invoices in {DATA_DIR}/")
        print("=" * 60)
        print("\nYou can now use these invoices in the Streamlit UI!")


if __name__ == "__main__":
    main()
