"""API endpoint for uploading and analyzing utility bills."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.bill_parsers import parse_ute_bill
from app.core.database import get_db
from app.services.bill_analyzer import BillAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/facturas", tags=["facturas"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/analyze")
async def analyze_bill(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a utility bill PDF and receive instant analysis.

    The PDF is processed in-memory. No personal data is stored.
    Only numerical data (consumption, charges, dates) is extracted.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande (máximo 5MB)")

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío")

    # Try parsing with available parsers
    # For MVP, only UTE is supported. Expand list as more parsers are added.
    bill_data = parse_ute_bill(contents)

    if bill_data is None:
        raise HTTPException(
            status_code=422,
            detail=(
                "No se pudo procesar la factura. "
                "Asegurate de subir un PDF de factura de UTE descargado "
                "del portal de UTE o recibido por email. "
                "Las facturas escaneadas (imágenes) no son compatibles por el momento."
            ),
        )

    # Analyze
    analyzer = BillAnalyzer(db)
    analysis = analyzer.analyze_ute(bill_data)

    # Build response (never include PII)
    return {
        "servicio": analysis.bill.servicio,
        "periodo": {
            "desde": analysis.bill.periodo_desde.isoformat(),
            "hasta": analysis.bill.periodo_hasta.isoformat(),
        },
        "consumo": {
            "valor": analysis.bill.consumo,
            "unidad": analysis.bill.consumo_unidad,
        },
        "cargos": {
            "fijo": analysis.bill.cargo_fijo,
            "variable": analysis.bill.cargo_variable,
            "total": analysis.bill.total,
        },
        "metricas": {
            "precio_unitario": analysis.bill.precio_unitario,
            "costo_diario": analysis.bill.costo_diario,
            "dias_facturados": analysis.bill.detalles.get("dias_facturados", 30),
            "consumo_diario_kwh": analysis.bill.detalles.get("consumo_diario_kwh", 0),
        },
        "comparacion": analysis.comparacion_tarifa_oficial,
        "percentil_consumo": analysis.percentil_consumo,
        "recomendaciones": [
            {
                "tipo": r.tipo,
                "titulo": r.titulo,
                "descripcion": r.descripcion,
                "ahorro_estimado": r.ahorro_estimado,
            }
            for r in analysis.recomendaciones
        ],
        "ahorro_potencial": analysis.ahorro_potencial,
    }
