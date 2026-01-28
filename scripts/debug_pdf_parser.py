#!/usr/bin/env python3
"""
Debug script para ver exactamente qué extrae el parser.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path("backend")))

from app.etl.pdf_parser import parse_ute_tariff_pdf

pdf_path = "backend/pdfs/ute/pliego_tarifario_2026_01.pdf"

print(f"Parseando: {pdf_path}\n")
records = parse_ute_tariff_pdf(pdf_path)

if records:
    print(f"✅ Extraídos {len(records)} registros:\n")
    for i, rec in enumerate(records, 1):
        print(f"{i}. {rec}")
else:
    print("❌ No se extrajo ningún registro")
