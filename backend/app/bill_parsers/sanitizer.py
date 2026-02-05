"""PII sanitization for bill text before logging or error reporting."""

import re

# Patterns for personal data found on Uruguayan utility bills
PII_PATTERNS = [
    # CI uruguaya: 1.234.567-8 or 12.345.678-9
    (r"\b\d{1,2}\.\d{3}\.\d{3}-\d\b", "[CI_REDACTED]"),
    # Titular/Cliente name lines
    (
        r"(?:Titular|Cliente|Nombre)\s*:?\s*[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+",
        "[NOMBRE_REDACTED]",
    ),
    # Address lines
    (r"(?:Dirección|Domicilio|Dir\.)\s*:?\s*.+", "[DIRECCION_REDACTED]"),
    # Account/service numbers (NIS, cuenta, servicio)
    (
        r"(?:NIS|N[uú]mero?\s+(?:de\s+)?(?:cliente|cuenta|servicio)|Cuenta)\s*:?\s*\d+",
        "[CUENTA_REDACTED]",
    ),
    # RUT
    (r"(?:RUT)\s*:?\s*\d+", "[RUT_REDACTED]"),
    # Email addresses
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_REDACTED]"),
    # Phone numbers (09X XXX XXX or 2XXX XXXX)
    (r"\b0\d{1,2}\s?\d{3}\s?\d{3,4}\b", "[TELEFONO_REDACTED]"),
]


def sanitize_text(text: str) -> str:
    """Strip PII from extracted bill text before any logging or error reporting."""
    sanitized = text
    for pattern, replacement in PII_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    return sanitized
