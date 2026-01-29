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
import re
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

            all_records = []
            min_score_threshold = 6  # Only accumulate tables with score >= 6 (high quality)

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

                    # BONUS: First column is "Tarifa" (indicates tariff codes table)
                    first_col = str(headers[0]).lower() if headers else ""
                    has_tarifa_col = "tarifa" in first_col
                    bonus_score = 5 if has_tarifa_col else 0

                    # REJECTION FILTERS: Financial/non-tariff tables
                    reject_keywords = [
                        "ingresos",
                        "egresos",
                        "deficit",
                        "superavit",
                        "escenario",
                        "miles de pesos",
                        "cobertura",
                        "caja",
                    ]
                    is_rejected = any(kw in flat_headers for kw in reject_keywords)

                    if is_rejected:
                        logger.debug(f"Page {page_idx}, Table {table_idx}: Rejected (financial document)")
                        continue

                    # Score-based validation (need at least medium + weak, or strict alone, or tarifa column)
                    score = (has_strict * 3) + (has_medium * 2) + (has_weak * 1) + bonus_score
                    if score < 3:
                        logger.debug(f"Page {page_idx}, Table {table_idx}: Score {score}/3 too low")
                        continue

                    logger.info(f"Found valid tariff table on page {page_idx}, table {table_idx} (score: {score})")

                    # Identify price column by analyzing headers
                    price_col_indices = []
                    for col_idx, header in enumerate(headers[1:], 1):  # Skip first column (tariff name)
                        header_lower = str(header).lower() if header else ""

                        # Skip voltage/tension columns
                        if any(kw in header_lower for kw in ["tensión", "tension", "kv", "nivel"]):
                            continue

                        # Prioritize price/energy columns
                        if any(kw in header_lower for kw in ["precio", "$/kwh", "kwh", "punta", "valle", "llano"]):
                            price_col_indices.append(col_idx)

                    # If no explicit price columns, use all numeric columns (fallback)
                    if not price_col_indices:
                        price_col_indices = list(range(1, len(headers)))

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
                        skip_patterns = [
                            "ingresos",
                            "egresos",
                            "ventas",
                            "deficit",
                            "superavit",
                            "saldo",
                            "compromiso",
                            "deuda",
                            "lunes",
                            "martes",
                            "miércoles",
                            "jueves",
                            "viernes",
                            "sábado",
                            "domingo",
                            "feriado",
                            "días de",
                        ]
                        if any(pattern in nombre.lower() for pattern in skip_patterns):
                            continue

                        # Get price value from identified price columns
                        valor_str = None
                        for col_idx in price_col_indices:
                            if col_idx < len(row):
                                cell_str = str(row[col_idx]).strip()
                                # Look for numeric values (with dots, commas, or $)
                                # Exclude voltage patterns (ranges with dash)
                                if cell_str and any(c.isdigit() for c in cell_str):
                                    # Skip if it's a voltage range (e.g., "0,230 - 0,400")
                                    if " - " in cell_str and "," in cell_str.split(" - ")[0]:
                                        continue
                                    valor_str = cell_str
                                    break

                        if not valor_str:
                            logger.debug(f"Row {row_idx}: No price value found for '{nombre}'")
                            continue

                        records.append(
                            {
                                "nombre": nombre,
                                "valor_str": valor_str,
                                "fecha": date.today(),
                                "fuente": f"PDF: {Path(pdf_path).name}",
                            }
                        )

                    if records:
                        logger.info(f"Extracted {len(records)} tariff records from page {page_idx}, table {table_idx}")

                        # Accumulate all tables with high score (>= threshold)
                        if score >= min_score_threshold:
                            all_records.extend(records)

            if all_records:
                logger.info(
                    f"Total extracted: {len(all_records)} tariff records from {len(set(r['nombre'] for r in all_records))} unique tariffs"
                )
                return all_records

            logger.warning(f"No valid tariff tables found in {Path(pdf_path).name}")
            return None

    except Exception as e:
        logger.error(f"Error parsing UTE tariff PDF {pdf_path}: {e}", exc_info=True)
        return None


def _parse_decimal(value: str) -> Optional[float]:
    if value is None:
        return None
    clean = str(value).replace("$", "").replace("UYU", "").replace(" ", "")
    clean = clean.replace(".", "").replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return None


def parse_ose_tariff_pdf(pdf_path: str) -> Optional[List[Dict]]:
    """
    Parse OSE tariff PDF and extract residential/commercial water tariffs.

    Expected to find rows mentioning "Residencial" and/or "Comercial" with
    values in $/m³ or similar notation. The parser is heuristic and falls back
    to text search when tables are not detected.

    Returns:
        List of extracted tariff records with keys: producto, valor_str, fecha, fuente
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"Parsing OSE PDF: {Path(pdf_path).name} ({len(pdf.pages)} pages)")

            for page_idx, page_obj in enumerate(pdf.pages):
                tables = page_obj.extract_tables() or []

                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue

                    records = []
                    for row in table[1:]:
                        if not row:
                            continue

                        row_text = " ".join(str(cell) for cell in row if cell)
                        row_lower = row_text.lower()

                        producto_key = None
                        if "residencial" in row_lower:
                            producto_key = "OSE_RESIDENCIAL"
                        elif "comercial" in row_lower or "no residencial" in row_lower:
                            producto_key = "OSE_COMERCIAL"

                        if not producto_key:
                            continue

                        numeric_cells = [cell for cell in row if cell and re.search(r"\d", str(cell))]
                        valor_str = None
                        for cell in numeric_cells:
                            candidate = str(cell)
                            if re.search(r"\d+[\.,]\d+", candidate) or re.search(r"\d{2,}", candidate):
                                valor_str = candidate
                                break

                        if not valor_str:
                            continue

                        records.append(
                            {
                                "producto": producto_key,
                                "valor_str": valor_str,
                                "fecha": date.today(),
                                "fuente": f"PDF: {Path(pdf_path).name}",
                            }
                        )

                    if records:
                        logger.info(
                            f"Extracted {len(records)} OSE tariff records from page {page_idx}, table {table_idx}"
                        )
                        return records

                # Fallback: parse text if no tables
                page_text = page_obj.extract_text() or ""
                if page_text:
                    candidates = []
                    for line in page_text.splitlines():
                        line_lower = line.lower()
                        producto_key = None
                        if "residencial" in line_lower:
                            producto_key = "OSE_RESIDENCIAL"
                        elif "comercial" in line_lower or "no residencial" in line_lower:
                            producto_key = "OSE_COMERCIAL"

                        if not producto_key:
                            continue

                        match = re.search(r"(\d+[\.,]\d+)", line)
                        if match:
                            candidates.append(
                                {
                                    "producto": producto_key,
                                    "valor_str": match.group(1),
                                    "fecha": date.today(),
                                    "fuente": f"PDF: {Path(pdf_path).name}",
                                }
                            )

                    if candidates:
                        logger.info(f"Extracted {len(candidates)} OSE tariff records from text on page {page_idx}")
                        return candidates

            logger.warning(f"No valid OSE tariff data found in {Path(pdf_path).name}")
            return None

    except Exception as e:
        logger.error(f"Error parsing OSE tariff PDF {pdf_path}: {e}", exc_info=True)
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
