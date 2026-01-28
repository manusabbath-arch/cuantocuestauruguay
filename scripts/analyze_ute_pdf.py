#!/usr/bin/env python3
"""
Script para analizar la estructura de PDFs de UTE.

Este script explora todas las páginas y tablas de los PDFs de UTE
para identificar cuál contiene las tarifas reales.

Uso:
    python scripts/analyze_ute_pdf.py
"""

import sys
from pathlib import Path

# Agregar backend al path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import pdfplumber


def analyze_pdf(pdf_path: str):
    """Analizar estructura de un PDF de UTE."""
    print(f"\n{'=' * 70}")
    print(f"ANALIZANDO: {Path(pdf_path).name}")
    print(f"{'=' * 70}\n")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Total de páginas: {len(pdf.pages)}\n")

            for page_idx, page_obj in enumerate(pdf.pages):
                tables = page_obj.extract_tables()

                if not tables:
                    continue

                print(f"📄 Página {page_idx + 1} - {len(tables)} tabla(s) encontrada(s)")
                print("-" * 70)

                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue

                    print(f"\n  📊 Tabla {table_idx + 1}:")
                    print(f"     Filas: {len(table)}")

                    # Mostrar headers
                    headers = table[0] if table else []
                    print(f"     Headers: {headers}")

                    # Analizar contenido de headers
                    flat_headers = " ".join(str(h).lower() for h in headers if h)

                    # Keywords de tarifas
                    tariff_keywords = ["bt1", "bt2", "bt3", "residencial", "comercial",
                                     "industrial", "kwh", "tarifa", "precio", "$/kwh"]
                    found_keywords = [kw for kw in tariff_keywords if kw in flat_headers]

                    if found_keywords:
                        print(f"     ✅ Keywords encontrados: {found_keywords}")
                    else:
                        print(f"     ⚠️  No keywords de tarifas")

                    # Mostrar primeras 3 filas
                    print(f"     Primeras filas:")
                    for i, row in enumerate(table[1:4], 1):
                        print(f"       {i}. {row}")

                    if len(table) > 5:
                        print(f"       ... ({len(table) - 4} filas más)")

                print()

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Ejecutar análisis de todos los PDFs de UTE."""
    pdf_dir = Path("backend/pdfs/ute")

    if not pdf_dir.exists():
        print(f"❌ Directorio no encontrado: {pdf_dir}")
        return 1

    pdfs = list(pdf_dir.glob("*.pdf"))

    if not pdfs:
        print(f"❌ No se encontraron PDFs en {pdf_dir}")
        return 1

    print(f"\n🔍 Encontrados {len(pdfs)} PDF(s) de UTE\n")

    for pdf_path in pdfs:
        analyze_pdf(str(pdf_path))

    return 0


if __name__ == "__main__":
    sys.exit(main())
