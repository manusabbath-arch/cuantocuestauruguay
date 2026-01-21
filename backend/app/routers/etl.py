from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.etl.combustibles import CombustiblesETL

router = APIRouter(prefix="/api/v1/etl", tags=["etl"])


@router.post("/run")
async def ejecutar_etl(db: Session = Depends(get_db)):
    """Ejecuta el proceso ETL manualmente (requiere autenticación en producción)"""
    try:
        etl = CombustiblesETL(db)
        result = await etl.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando ETL: {str(e)}")


@router.get("/status")
async def obtener_estado():
    """Obtiene el estado del último proceso ETL"""
    # TODO: Implementar tracking de ejecuciones ETL
    return {
        "message": "ETL status endpoint - to be implemented",
        "last_run": None
    }
