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

    This parser is designed for "Pliego Tarifario" documents from UTE
    that contain actual electricity tariff rates by category (BT1, BT2, etc.).

    Expected table structure:
    - Column 1: Tariff category (e.g., "Residencial BT1", "Comercial BT3")
    - Column 2+: Rate values ($/kWh)

    Keywords that indicate a valid tariff table:
    - Strict: "BT1", "BT2", "BT3", "MT", "AT" (voltage categories)
    - Medium: "residencial", "comercial", "industrial"
    - Weak: "$/kWh", "precio", "tarifa"

    Args:
        pdf_path: Path to UTE tariff PDF (ideally "Pliego Tarifario")

    Returns:
        List of extracted tariff records with keys: nombre, valor_str, fecha, fuente
        Returns None if no valid tariff table is found

    Note:
        Financial documents (e.g., "Escenarios de Aumento") will be rejected
        as they don't contain actual tariff rates by category.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"Parsing UTE PDF: {Path(pdf_path).name} ({len(pdf.pages)} pages)")

            # Try multiple pages (tariffs often span pages)
            for page_idx, page_obj in enumerate(pdf.pages):
                tables = page_obj.extract_tables()
                if not tables:
                    continue

                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 3:  # Need at least header + 2 data rows
                        continue

                    # Extract headers and flatten to string
                    headers = table[0] if table else []
                    flat_headers = " ".join(str(h).lower() for h in headers if h)

                    # STRICT VALIDATION: Must contain voltage category keywords
                    strict_keywords = ["bt1", "bt2", "bt3", "mt", "at"]
                    has_strict = any(kw in flat_headers for kw in strict_keywords)

                    # MEDIUM VALIDATION: Customer type keywords
                    medium_keywords = ["residencial", "comercial", "industrial"]
                    has_medium = any(kw in flat_headers for kw in medium_keywords)

                    # WEAK VALIDATION: Generic tariff keywords
                    weak_keywords = ["$/kwh", "precio", "kwh"]
                    has_weak = any(kw in flat_headers for kw in weak_keywords)

                    # REJECTION FILTERS: Financial/non-tariff tables
                    reject_keywords = ["ingresos", "egresos", "deficit", "superavit",
                                     "escenario", "miles de pesos", "cobertura", "caja"]
                    is_rejected = any(kw in flat_headers for kw in reject_keywords)

                    if is_rejected:
                        logger.debug(f"Page {page_idx}, Table {table_idx}: Rejected (financial document)")
                        continue

                    # Score-based validation (need at least medium + weak, or strict alone)
                    score = (has_strict * 3) + (has_medium * 2) + (has_weak * 1)
                    if score < 3:
                        logger.debug(f"Page {page_idx}, Table {table_idx}: Score {score}/3 too low")
                        continue

                    logger.info(f"Found valid tariff table on page {page_idx}, table {table_idx} (score: {score})")

                    # Extract tariff records
                    records = []
                    for row_idx, row in enumerate(table[1:], 1):
                        if not row or len(row) < 2:
                            continue

                        # Get tariff name (first column)
                        nombre = str(row[0]).strip()

                        # Skip empty rows or subtotals
                        if not nombre or nombre.lower() in ["", "total", "subtotal", "none"]:
                            continue

                        # Skip rows that are clearly not tariffs
                        skip_patterns = ["ingresos", "egresos", "ventas", "deficit",
                                       "superavit", "saldo", "compromiso", "deuda"]
                        if any(pattern in nombre.lower() for pattern in skip_patterns):
                            continue

                        # Get price value (second column, or search for numeric)
                        valor_str = None
                        for cell in row[1:]:
                            cell_str = str(cell).strip()
                            # Look for numeric values (with dots, commas, or $)
                            if cell_str and any(c.isdigit() for c in cell_str):
                                valor_str = cell_str
                                break

                        if not valor_str:
                            logger.debug(f"Row {row_idx}: No price value found for '{nombre}'")
                            continue

                        records.append({
                            "nombre": nombre,
                            "valor_str": valor_str,
                            "fecha": date.today(),
                            "fuente": f"PDF: {Path(pdf_path).name}",
                        })

                    if records:
                        logger.info(f"Extracted {len(records)} tariff records from page {page_idx}")
                        return records

            logger.warning(f"No valid tariff tables found in {Path(pdf_path).name}")
            return None

    except Exception as e:
        logger.error(f"Error parsing UTE tariff PDF {pdf_path}: {e}", exc_info=True)
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
