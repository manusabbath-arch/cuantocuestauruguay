"""
PDF utilities for extracting tariff data from URSEA documents.

This module provides helpers for:
1. Downloading URSEA PDF documents
2. Parsing table data from PDFs
3. Extracting tariff information

Note: URSEA website uses JavaScript; PDFs should be downloaded manually or via Playwright.
This module focuses on parsing already-downloaded PDFs.
"""

import logging
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

import pdfplumber

logger = logging.getLogger(__name__)


def extract_table_from_pdf(pdf_path: str, page: int = 0, table_idx: int = 0) -> Optional[List[Dict]]:
    """
    Extract a table from a PDF using pdfplumber.

    Args:
        pdf_path: Path to PDF file
        page: Page number (0-indexed)
        table_idx: Table index on page (0-indexed)

    Returns:
        List of dictionaries representing table rows, or None if extraction fails
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page >= len(pdf.pages):
                logger.warning(f"Page {page} not found in {pdf_path}")
                return None

            page_obj = pdf.pages[page]
            tables = page_obj.extract_tables()

            if not tables or table_idx >= len(tables):
                logger.warning(f"Table {table_idx} not found on page {page}")
                return None

            table = tables[table_idx]

            # Convert table (list of lists) to list of dicts
            if not table or len(table) < 2:
                return None

            headers = table[0]
            rows = []
            for row in table[1:]:
                row_dict = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
                rows.append(row_dict)

            return rows

    except Exception as e:
        logger.error(f"Error extracting table from {pdf_path}: {e}")
        return None


def extract_text_from_pdf(pdf_path: str, page: int = 0) -> Optional[str]:
    """
    Extract all text from a specific page of a PDF.

    Args:
        pdf_path: Path to PDF file
        page: Page number (0-indexed)

    Returns:
        Extracted text or None if extraction fails
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page >= len(pdf.pages):
                logger.warning(f"Page {page} not found in {pdf_path}")
                return None

            return pdf.pages[page].extract_text()

    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return None


def parse_ute_tariff_pdf(pdf_path: str) -> Optional[List[Dict]]:
    """
    Parse UTE tariff PDF and extract tariff data.

    Attempts to find tariff table and extract structured data.
    Expected columns: Tariff name, Rate ($/kWh), Effective date

    Args:
        pdf_path: Path to UTE tariff PDF

    Returns:
        List of extracted tariff records with keys: nombre, valor, fecha
    """
    tables = None

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Try multiple pages (tariffs often span pages)
            for page_idx, page_obj in enumerate(pdf.pages):
                tables = page_obj.extract_tables()
                if tables:
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 1:
                            # Check if this looks like a tariff table
                            # Look for columns with "tariff", "rate", "$", "kWh"
                            flat_headers = " ".join(str(h) for h in table[0]).lower()
                            if any(x in flat_headers for x in ["tarifa", "tariff", "tasa", "rate", "kwh", "$"]):
                                logger.info(f"Found potential tariff table on page {page_idx}, table {table_idx}")
                                records = []
                                for row in table[1:]:
                                    if row and len(row) >= 2:
                                        # Simple heuristic: first col = name, second col = value
                                        records.append(
                                            {
                                                "nombre": str(row[0]).strip(),
                                                "valor_str": str(row[1]).strip(),
                                                "fecha": date.today(),
                                                "fuente": f"PDF: {Path(pdf_path).name}",
                                            }
                                        )
                                if records:
                                    return records

    except Exception as e:
        logger.error(f"Error parsing UTE tariff PDF {pdf_path}: {e}")

    return None


def list_pdfs_in_directory(dir_path: str) -> List[str]:
    """
    List all PDF files in a directory.

    Args:
        dir_path: Directory path

    Returns:
        List of absolute paths to PDF files
    """
    path = Path(dir_path)
    if not path.exists():
        logger.warning(f"Directory {dir_path} not found")
        return []

    return [str(p) for p in path.glob("*.pdf")]
