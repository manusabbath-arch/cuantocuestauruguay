"""Analysis engine for utility bills. Compares user data against official tariffs."""

import logging

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.bill_parsers.base import BillAnalysis, BillData, Recomendacion
from app.models.models import Precio, Producto

logger = logging.getLogger(__name__)

# Average residential consumption in Uruguay (source: UTE annual reports)
UTE_CONSUMO_PROMEDIOS = {
    "muy_bajo": 100,  # kWh/month
    "bajo": 150,
    "promedio": 225,  # National residential average
    "alto": 400,
    "muy_alto": 600,
}

# Threshold above which Doble Horario becomes advantageous over Residencial Simple.
UMBRAL_DOBLE_HORARIO_KWH = 350

# Typical appliance consumption in Uruguay (kWh/month, assumes average usage)
# Source: UTE energy efficiency guides
ELECTRODOMESTICOS_CONSUMO = {
    "Calefón eléctrico (100L)": 150,
    "Aire acondicionado (uso diario, 8h)": 120,
    "Heladera con freezer": 45,
    "Lavarropas (4 lavados/sem)": 20,
    "TV LED 42\" (6h/día)": 15,
    "Iluminación LED (casa entera)": 10,
    "Standby total (aparatos varios)": 15,
}


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
                self.db.query(Precio)
                .filter(Precio.producto_id == producto.id)
                .order_by(desc(Precio.fecha))
                .first()
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

    def _generar_recomendaciones_ute(
        self, bill: BillData, percentil: int
    ) -> list[Recomendacion]:
        """Generate personalized recommendations based on bill data."""
        recomendaciones = []
        tarifa_lower = bill.tarifa_tipo.lower()
        is_simple = "simple" in tarifa_lower or "no identificada" in tarifa_lower

        # Recommendation 1: Tariff switch — Doble Horario
        if is_simple and bill.consumo >= UMBRAL_DOBLE_HORARIO_KWH:
            ahorro_est = round(bill.total * 0.12, 0)
            recomendaciones.append(
                Recomendacion(
                    tipo="cambio_tarifa",
                    titulo="Considerar cambio a Doble Horario",
                    descripcion=(
                        f"Tu consumo de {bill.consumo:.0f} kWh/mes es alto. "
                        f"Con la tarifa Doble Horario podrías ahorrar ~"
                        f"${ahorro_est:.0f}/mes si concentrás el uso en "
                        f"horario valle (23:00 a 07:00 y fines de semana). "
                        f"Eso es ${ahorro_est * 12:.0f} al año. "
                        f"El trámite se hace online en la web de UTE."
                    ),
                    ahorro_estimado=ahorro_est,
                )
            )

        # Recommendation 2: High consumption — specific appliance breakdown
        if percentil >= 75:
            # Build appliance breakdown relative to user's consumption
            breakdown_lines = []
            total_estimado = 0
            for aparato, kwh in ELECTRODOMESTICOS_CONSUMO.items():
                if total_estimado + kwh <= bill.consumo * 1.1:
                    costo = round(kwh * bill.precio_unitario, 0)
                    breakdown_lines.append(f"• {aparato}: ~{kwh} kWh (${costo}/mes)")
                    total_estimado += kwh

            desc_text = (
                f"Tu consumo de {bill.consumo:.0f} kWh/mes está en el "
                f"percentil {percentil} (más que el {percentil}% de los "
                f"hogares uruguayos). El promedio nacional es ~"
                f"{UTE_CONSUMO_PROMEDIOS['promedio']} kWh/mes.\n\n"
                f"Estimación de consumo por electrodoméstico:\n"
                + "\n".join(breakdown_lines[:5])
            )

            # If calefón is a likely culprit (>300 kWh), add specific tip
            if bill.consumo >= 300:
                ahorro_calefon = round(
                    ELECTRODOMESTICOS_CONSUMO["Calefón eléctrico (100L)"]
                    * bill.precio_unitario
                    * 0.3,
                    0,
                )
                desc_text += (
                    f"\n\nTip: Bajar el termostato del calefón de 60°C a "
                    f"45°C puede ahorrarte ~${ahorro_calefon}/mes sin "
                    f"perder confort."
                )
                recomendaciones.append(
                    Recomendacion(
                        tipo="reduccion_consumo",
                        titulo="Tu consumo es superior al promedio",
                        descripcion=desc_text,
                        ahorro_estimado=ahorro_calefon,
                    )
                )
            else:
                recomendaciones.append(
                    Recomendacion(
                        tipo="reduccion_consumo",
                        titulo="Tu consumo es superior al promedio",
                        descripcion=desc_text,
                    )
                )

        # Recommendation 3: Low consumption + wrong tariff
        if percentil <= 25 and "doble" in tarifa_lower:
            # Estimate how much they overpay on cargo fijo
            sobrecosto_est = round(bill.cargo_fijo * 0.3, 0) if bill.cargo_fijo else None
            recomendaciones.append(
                Recomendacion(
                    tipo="cambio_tarifa",
                    titulo="Considerar volver a Residencial Simple",
                    descripcion=(
                        f"Tu consumo de {bill.consumo:.0f} kWh/mes es bajo. "
                        f"La tarifa Doble Horario tiene un cargo fijo mayor "
                        f"(${bill.cargo_fijo:.0f}) que puede no compensarse "
                        f"con tu nivel de consumo. Con Residencial Simple "
                        f"podrías pagar menos en cargo fijo."
                    ),
                    ahorro_estimado=sobrecosto_est,
                )
            )

        # Recommendation 4: Standby consumption awareness (medium consumers)
        if 200 <= bill.consumo <= 400 and percentil >= 50:
            standby_kwh = ELECTRODOMESTICOS_CONSUMO["Standby total (aparatos varios)"]
            ahorro_standby = round(standby_kwh * bill.precio_unitario, 0)
            recomendaciones.append(
                Recomendacion(
                    tipo="reduccion_consumo",
                    titulo="Consumo fantasma (standby)",
                    descripcion=(
                        f"Los aparatos en standby (TV, microondas, cargadores) "
                        f"consumen ~{standby_kwh} kWh/mes sin que los uses. "
                        f"Usando zapatillas con interruptor podrías ahorrar "
                        f"~${ahorro_standby}/mes (${ahorro_standby * 12}/año)."
                    ),
                    ahorro_estimado=ahorro_standby,
                )
            )

        # Recommendation 5: Cost per day insight (always shown)
        dias = bill.detalles.get("dias_facturados", 30)
        costo_anual = round(bill.total * 12 / (dias / 30), 0) if dias else bill.total * 12
        recomendaciones.append(
            Recomendacion(
                tipo="informativo",
                titulo="Tu costo diario de electricidad",
                descripcion=(
                    f"Estás pagando ${bill.costo_diario:.0f} por día "
                    f"(${bill.total:.0f} en {dias} días). "
                    f"Tu precio efectivo es ${bill.precio_unitario:.2f}/kWh. "
                    f"Proyección anual: ~${costo_anual:,.0f}."
                ),
            )
        )

        return recomendaciones
