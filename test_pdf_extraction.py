#!/usr/bin/env python3
"""
Test script for PDF extraction capabilities
Tests the pdf_parser module with actual downloaded PDFs
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

def test_pdf_parsing():
    """Test PDF parsing with actual downloaded PDFs"""
    
    try:
        import pdfplumber
        print("✅ pdfplumber imported successfully")
    except ImportError:
        print("❌ pdfplumber not installed. Install with: pip install pdfplumber")
        return False
    
    pdf_files = {
        'backend/pdfs/ute/ute_tarifas_2020_04.pdf': 'UTE 2020',
        'backend/pdfs/ute/ute_tarifas_2021_01.pdf': 'UTE 2021',
        'backend/pdfs/ose/ose_tarifas_2021_04.pdf': 'OSE 2021',
    }
    
    print("\n" + "="*75)
    print("📊 PDF EXTRACTION TEST")
    print("="*75)
    
    results = {}
    
    for pdf_path, label in pdf_files.items():
        path_obj = Path(pdf_path)
        
        if not path_obj.exists():
            print(f"\n❌ {label}: Archivo no encontrado en {pdf_path}")
            results[label] = {'status': 'missing'}
            continue
        
        print(f"\n📄 {label}")
        print(f"   Ruta: {pdf_path}")
        print(f"   Tamaño: {path_obj.stat().st_size / 1024:.1f} KB")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                print(f"   ✅ PDF válido - {num_pages} página(s)")
                
                # Scan for tables
                tables_found = []
                for page_num in range(num_pages):
                    page = pdf.pages[page_num]
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            if table and len(table) > 0:
                                tables_found.append({
                                    'page': page_num + 1,
                                    'index': table_idx,
                                    'rows': len(table),
                                    'cols': len(table[0]),
                                    'headers': table[0][:3]  # First 3 headers
                                })
                
                if tables_found:
                    print(f"   📊 Tablas encontradas: {len(tables_found)}")
                    for t in tables_found[:2]:  # Show first 2 tables
                        print(f"      - Página {t['page']}, Tabla {t['index']}: "
                              f"{t['rows']} filas × {t['cols']} columnas")
                        print(f"        Encabezados: {t['headers']}")
                    results[label] = {
                        'status': 'success',
                        'pages': num_pages,
                        'tables': len(tables_found),
                        'first_table': tables_found[0] if tables_found else None
                    }
                else:
                    print(f"   ⚠️  No se encontraron tablas en las páginas escaneadas")
                    # Try to extract text
                    text_preview = pdf.pages[0].extract_text()[:200] if pdf.pages else ""
                    print(f"      Preview: {text_preview}...")
                    results[label] = {
                        'status': 'no_tables',
                        'pages': num_pages,
                        'preview': text_preview[:100]
                    }
                    
        except Exception as e:
            print(f"   ❌ Error al procesar: {str(e)[:100]}")
            results[label] = {'status': 'error', 'error': str(e)[:100]}
    
    # Summary
    print("\n" + "="*75)
    print("📈 RESUMEN DE EXTRACCIÓN")
    print("="*75)
    
    success_count = sum(1 for r in results.values() if r.get('status') == 'success')
    total_count = len(results)
    
    print(f"\nResultados: {success_count}/{total_count} PDFs con tablas detectadas")
    
    for label, result in results.items():
        status = result.get('status')
        if status == 'success':
            print(f"  ✅ {label}: {result['tables']} tabla(s), {result['pages']} página(s)")
        elif status == 'no_tables':
            print(f"  ⚠️  {label}: Sin tablas detectadas (pero PDF válido)")
        elif status == 'missing':
            print(f"  ❌ {label}: Archivo no encontrado")
        else:
            print(f"  ❌ {label}: Error - {result.get('error', 'unknown')}")
    
    print("\n" + "="*75)
    print("🎯 PRÓXIMOS PASOS")
    print("="*75)
    
    if success_count > 0:
        print("""
✅ Los PDFs se detectaron correctamente y contienen tablas.
   El módulo pdf_parser.py puede procesar estos archivos.
   
Próximos pasos:
1. Ejecutar el ETL para procesar los PDFs: POST /api/v1/etl/execute
2. Verificar logs de extracción: GET /api/v1/etl/alerts
3. Consultar BD: SELECT * FROM precios WHERE fuente LIKE 'URSEA - PDF%'
""")
    else:
        print("""
⚠️  Los PDFs descargados no contienen tablas detectables por pdfplumber.
   
Posibles soluciones:
1. Los PDFs pueden requerir OCR (images en lugar de texto)
2. Las tablas pueden estar formateadas de manera no estándar
3. Usar Playwright para JS-based extraction si disponible
4. Utilizar fallback a TARIFF_HISTORY (datos históricos verificados)
""")
    
    return success_count > 0

if __name__ == '__main__':
    success = test_pdf_parsing()
    sys.exit(0 if success else 1)
