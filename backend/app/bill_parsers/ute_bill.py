"""Parser for UTE (electricity) bills in PDF format."""

import io
import logging
import re
from datetime import date, datetime
from typing import Optional

import pdfplumber

from app.bill_parsers.base import BillData
from app.bill_parsers.sanitizer import sanitize_text
from app.etl.pdf_parser import _parse_decimal

logger = logging.getLogger(__name__)


# Regex patterns based on actual UTE bill field labels.
# UTE bills use: "Consumo activo (kWh)", "Tarifa aplicada", "Período de consumo",
# "Cargo fijo", "Cargo por energía", "Total cargos del mes", "Importe total".
PATTERNS = {
    "consumo_kwh": [
        r"Consumo\s+activo\s*\(?\s*kWh\s*\)?\s*:?\s*([\d\.,]+)",
        r"Consumo\s*:?\s*([\d\.,]+)\s*kWh",
        r"Energ[ií]a\s+activa\s*:?\s*([\d\.,]+)\s*kWh",
        r"([\d\.,]+)\s*kWh",
    ],
    "tarifa_tipo": [
        r"Tarifa\s+aplicada\s*:?\s*(.+?)(?:\n|$)",
        r"Tarifa\s*:?\s*(Residencial\s+\w+|Simple\s+\w+|Doble\s+Horario|Triple\s+Horario|Inteligente)",
        r"Categor[ií]a\s*:?\s*(Residencial\s+\w+|Doble\s+Horario|Triple\s+Horario)",
    ],
    "cargo_fijo": [
        r"Cargo\s+fijo\s*:?\s*\$?\s*([\d\.,]+)",
        r"Cargo\s+fijo\s+mensual\s*:?\s*\$?\s*([\d\.,]+)",
        r"Potencia\s+contratada\s*.*?\$?\s*([\d\.,]+)",
    ],
    "cargo_variable": [
        r"Cargo\s+(?:por\s+)?energ[ií]a\s*:?\s*\$?\s*([\d\.,]+)",
        r"Energ[ií]a\s+activa\s*:?\s*\$?\s*([\d\.,]+)",
        r"Consumo\s+energ[ií]a\s*:?\s*\$?\s*([\d\.,]+)",
    ],
    "total": [
        r"Total\s+cargos\s+del\s+mes\s*:?\s*\$?\s*([\d\.,]+)",
        r"Importe\s+total\s*:?\s*\$?\s*([\d\.,]+)",
        r"TOTAL\s+A\s+PAGAR\s*:?\s*\$?\s*([\d\.,]+)",
        r"Total\s+factura\s*:?\s*\$?\s*([\d\.,]+)",
    ],
    "periodo": [
        r"Per[ií]odo\s+de\s+consumo\s+el[eé]ctrico\s*:?\s*(\d{2}/\d{2}/\d{4})\s*(?:a|al|hasta|-)\s*(\d{2}/\d{2}/\d{4})",
        r"Per[ií]odo\s*:?\s*(\d{2}/\d{2}/\d{4})\s*(?:a|al|hasta|-)\s*(\d{2}/\d{2}/\d{4})",
        r"Desde\s*:?\s*(\d{2}/\d{2}/\d{4})\s*(?:a|al|hasta|-)\s*(\d{2}/\d{2}/\d{4})",
        r"(\d{2}/\d{2}/\d{4})\s*(?:a|al|hasta|-)\s*(\d{2}/\d{2}/\d{4})",
    ],
}


def _extract_field(text: str, patterns: list[str]) -> Optional[str]:
    """Try each regex pattern in order, return first match group 1."""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_periodo(text: str) -> tuple[Optional[date], Optional[date]]:
    """Extract billing period dates from text."""
    for pattern in PATTERNS["periodo"]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                desde = datetime.strptime(match.group(1), "%d/%m/%Y").date()
                hasta = datetime.strptime(match.group(2), "%d/%m/%Y").date()
                return desde, hasta
            except ValueError:
                continue
    return None, None


def _detect_ute_bill(text: str) -> bool:
    """Check if PDF text looks like a UTE electricity bill."""
    text_lower = text.lower()
    ute_indicators = [
        "ute" in text_lower,
        "usinas" in text_lower or "transmisiones" in text_lower,
        "kwh" in text_lower,
        "consumo" in text_lower and ("eléctrico" in text_lower or "electrico" in text_lower or "activo" in text_lower),
    ]
    # Need at least 2 indicators to be confident
    return sum(ute_indicators) >= 2


def parse_ute_bill(pdf_bytes: bytes) -> Optional[BillData]:
    """
    Parse a UTE electricity bill PDF and extract structured data.

    The PDF is processed entirely in memory. No personal data (name, address,
    account number) is extracted or stored.

    Args:
        pdf_bytes: Raw PDF file content

    Returns:
        BillData with extracted consumption and charge data, or None if parsing fails
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # Extract text from all pages
            all_text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                all_text += page_text + "\n"

            if not all_text.strip():
                logger.warning("PDF has no extractable text (may be a scanned image)")
                return None

            # Verify this is a UTE bill
            if not _detect_ute_bill(all_text):
                logger.info("PDF does not appear to be a UTE bill")
                return None

            # Extract fields
            consumo_str = _extract_field(all_text, PATTERNS["consumo_kwh"])
            tarifa_str = _extract_field(all_text, PATTERNS["tarifa_tipo"])
            cargo_fijo_str = _extract_field(all_text, PATTERNS["cargo_fijo"])
            cargo_variable_str = _extract_field(all_text, PATTERNS["cargo_variable"])
            total_str = _extract_field(all_text, PATTERNS["total"])
            periodo_desde, periodo_hasta = _extract_periodo(all_text)

            # Parse numeric values using existing Uruguayan format parser
            consumo = _parse_decimal(consumo_str) if consumo_str else None
            cargo_fijo = _parse_decimal(cargo_fijo_str) if cargo_fijo_str else None
            cargo_variable = _parse_decimal(cargo_variable_str) if cargo_variable_str else None
            total = _parse_decimal(total_str) if total_str else None

            # Minimum required fields: consumo and total
            if consumo is None or total is None:
                logger.warning(
                    "Could not extract minimum required fields from UTE bill. "
                    "Extracted: consumo=%s, total=%s (sanitized text available in debug)",
                    consumo_str is not None,
                    total_str is not None,
                )
                return None

            # Use defaults for optional fields
            if cargo_fijo is None:
                cargo_fijo = 0.0
            if cargo_variable is None:
                # Estimate: total - cargo_fijo
                cargo_variable = max(0.0, total - cargo_fijo)
            if tarifa_str is None:
                tarifa_str = "No identificada"
            if periodo_desde is None or periodo_hasta is None:
                # Default to current month if period not found
                today = date.today()
                periodo_desde = periodo_desde or today.replace(day=1)
                periodo_hasta = periodo_hasta or today

            # Compute derived metrics
            dias = max(1, (periodo_hasta - periodo_desde).days)
            precio_unitario = cargo_variable / consumo if consumo > 0 else 0.0
            costo_diario = total / dias

            return BillData(
                servicio="UTE",
                periodo_desde=periodo_desde,
                periodo_hasta=periodo_hasta,
                consumo=consumo,
                consumo_unidad="kWh",
                cargo_fijo=cargo_fijo,
                cargo_variable=cargo_variable,
                total=total,
                tarifa_tipo=tarifa_str,
                precio_unitario=round(precio_unitario, 2),
                costo_diario=round(costo_diario, 2),
                detalles={
                    "dias_facturados": dias,
                    "consumo_diario_kwh": round(consumo / dias, 1),
                },
            )

    except Exception as e:
        # Sanitize any text that might contain PII before logging
        safe_msg = sanitize_text(str(e))
        logger.error("Error parsing UTE bill: %s", safe_msg)
        return None
