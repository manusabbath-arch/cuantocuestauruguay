"""Analysis engine for utility bills. Compares user data against official tariffs."""

import logging

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.bill_parsers.base import BillAnalysis, BillData, Recomendacion
from app.models.models import Precio, Producto

logger = logging.getLogger(__name__)

# Average residential consumption in Uruguay (source: UTE annual reports)
# These are hardcoded benchmarks for the MVP; in the future, could be sourced from a DB table.
UTE_CONSUMO_PROMEDIOS = {
    "muy_bajo": 100,  # kWh/month
    "bajo": 150,
    "promedio": 225,  # National residential average
    "alto": 400,
    "muy_alto": 600,
}

# Threshold above which Doble Horario becomes advantageous over Residencial Simple.
# Based on UTE tariff structure analysis: Doble Horario has lower off-peak rates
# that compensate the higher peak rates when total consumption is high enough.
UMBRAL_DOBLE_HORARIO_KWH = 350


class BillAnalyzer:
    """Analyzes parsed bill data against official tariffs and provides recommendations."""

    def __init__(self, db: Session):
        self.db = db

    def analyze_ute(self, bill: BillData) -> BillAnalysis:
        """Analyze a UTE electricity bill."""
        comparacion = self._comparar_tarifa_ute(bill)
        percentil = self._calcular_percentil_consumo(bill.consumo)
        recomendaciones = self._generar_recomendaciones_ute(bill, percentil)
        ahorro = sum(r.ahorro_estimado or 0 for r in recomendaciones)

        return BillAnalysis(
            bill=bill,
            comparacion_tarifa_oficial=comparacion,
            percentil_consumo=percentil,
            recomendaciones=recomendaciones,
            ahorro_potencial=round(ahorro, 2),
        )

    def _comparar_tarifa_ute(self, bill: BillData) -> dict:
        """Compare user's effective rate against official UTE tariffs from the DB."""
        # Get official UTE tariff rates from database
        productos_ute = (
            self.db.query(Producto)
            .filter(
                Producto.categoria == "Servicios Públicos - Electricidad",
                Producto.activo.is_(True),
            )
            .all()
        )

        tarifas_oficiales = {}
        for producto in productos_ute:
            ultimo_precio = (
                self.db.query(Precio).filter(Precio.producto_id == producto.id).order_by(desc(Precio.fecha)).first()
            )
            if ultimo_precio:
                tarifas_oficiales[producto.nombre] = {
                    "valor": float(ultimo_precio.valor),
                    "fecha": ultimo_precio.fecha.isoformat(),
                    "unidad": producto.unidad,
                }

        return {
            "tu_precio_kwh": bill.precio_unitario,
            "tarifas_oficiales": tarifas_oficiales,
            "tu_tarifa": bill.tarifa_tipo,
        }

    def _calcular_percentil_consumo(self, consumo_kwh: float) -> int:
        """Calculate where user's consumption falls relative to national averages."""
        promedios = UTE_CONSUMO_PROMEDIOS
        if consumo_kwh <= promedios["muy_bajo"]:
            return 10
        elif consumo_kwh <= promedios["bajo"]:
            return 25
        elif consumo_kwh <= promedios["promedio"]:
            return 50
        elif consumo_kwh <= promedios["alto"]:
            return 75
        else:
            return 95

    def _generar_recomendaciones_ute(self, bill: BillData, percentil: int) -> list[Recomendacion]:
        """Generate personalized recommendations based on bill data."""
        recomendaciones = []

        # Recommendation 1: Tariff switch
        tarifa_lower = bill.tarifa_tipo.lower()
        is_simple = "simple" in tarifa_lower or "no identificada" in tarifa_lower
        if is_simple and bill.consumo >= UMBRAL_DOBLE_HORARIO_KWH:
            # Estimate savings: Doble Horario saves ~10-15% for high consumers
            ahorro_est = round(bill.total * 0.12, 0)
            recomendaciones.append(
                Recomendacion(
                    tipo="cambio_tarifa",
                    titulo="Considerar cambio a Doble Horario",
                    descripcion=(
                        f"Tu consumo de {bill.consumo:.0f} kWh/mes es alto. "
                        f"Con la tarifa Doble Horario podrías ahorrar aproximadamente "
                        f"${ahorro_est:.0f}/mes si concentrás el uso en horario valle "
                        f"(23:00 a 07:00 y fines de semana)."
                    ),
                    ahorro_estimado=ahorro_est,
                )
            )

        # Recommendation 2: High consumption alert
        if percentil >= 75:
            recomendaciones.append(
                Recomendacion(
                    tipo="reduccion_consumo",
                    titulo="Tu consumo es superior al promedio",
                    descripcion=(
                        f"Tu consumo de {bill.consumo:.0f} kWh/mes está en el percentil {percentil} "
                        f"(consumís más que el {percentil}% de los hogares uruguayos). "
                        f"El promedio nacional es ~{UTE_CONSUMO_PROMEDIOS['promedio']} kWh/mes. "
                        f"Revisá electrodomésticos que consuman mucho en standby, calefones "
                        f"eléctricos o aires acondicionados."
                    ),
                )
            )

        # Recommendation 3: Low consumption - validate tariff
        if percentil <= 25 and "doble" in tarifa_lower:
            recomendaciones.append(
                Recomendacion(
                    tipo="cambio_tarifa",
                    titulo="Considerar volver a Residencial Simple",
                    descripcion=(
                        f"Tu consumo de {bill.consumo:.0f} kWh/mes es bajo. "
                        f"La tarifa Doble Horario tiene un cargo fijo mayor que puede "
                        f"no compensarse con tu nivel de consumo. Evaluá si Residencial "
                        f"Simple te resultaría más económica."
                    ),
                )
            )

        # Recommendation 4: Cost per day insight (always shown)
        recomendaciones.append(
            Recomendacion(
                tipo="informativo",
                titulo="Tu costo diario de electricidad",
                descripcion=(
                    f"Estás pagando ${bill.costo_diario:.0f} por día en electricidad "
                    f"(${bill.total:.0f} en {bill.detalles.get('dias_facturados', 30)} días). "
                    f"Tu precio efectivo es ${bill.precio_unitario:.2f}/kWh."
                ),
            )
        )

        return recomendaciones
